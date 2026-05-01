# -*- coding: utf-8 -*-
"""
TDD-Loop entry point.

Usage:
    python -m tdd_loop.run path/to/feature_list.json [--spec SPEC.md]
                            [--model MODEL] [--max-iter N]
                            [--environment ENV] [--env-arg k=v]...
                            [--project-dir DIR] [--auto-resume]
"""

import argparse
import atexit
import importlib
import io
import logging
import os
import signal
import subprocess
import sys
import time
from pathlib import Path


def _kill_process_tree(pid: int, logger: logging.Logger) -> None:
    if pid <= 0:
        return
    if sys.platform == "win32":
        try:
            r = subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                capture_output=True, text=True, timeout=10,
            )
            logger.info(f"  taskkill PID={pid}: rc={r.returncode}")
        except (subprocess.TimeoutExpired, OSError) as e:
            logger.warning(f"  taskkill failed: {e}")
    else:
        try:
            pgid = os.getpgid(pid)
            os.killpg(pgid, signal.SIGTERM)
            time.sleep(1)
            os.killpg(pgid, signal.SIGKILL)
        except (ProcessLookupError, OSError):
            pass


def _wait_pid_dead(pid: int, timeout: float = 10.0) -> bool:
    from tdd_loop.lockfile import _is_pid_alive
    deadline = time.time() + timeout
    while time.time() < deadline:
        if not _is_pid_alive(pid):
            return True
        time.sleep(0.3)
    return False


def _load_environment(env_name: str, env_args: dict):
    """Locate a `build(**kwargs)` factory under environments/<env_name>.py
    and instantiate it."""
    if not env_name:
        from tdd_loop.environment import NullEnvironment
        return NullEnvironment()
    try:
        mod = importlib.import_module(f"environments.{env_name}")
    except ModuleNotFoundError:
        root = Path(__file__).resolve().parent.parent
        sys.path.insert(0, str(root))
        mod = importlib.import_module(f"environments.{env_name}")
    if "build" not in dir(mod):
        raise SystemExit(f"Environment module '{env_name}' has no build() factory")
    return mod.build(**env_args)


def _parse_env_args(pairs: list[str]) -> dict:
    out = {}
    for p in pairs or []:
        if "=" not in p:
            raise SystemExit(f"--env-arg expects key=value, got: {p}")
        k, v = p.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def main():
    parser = argparse.ArgumentParser(
        description="TDD-Loop — spec-driven iterative TDD agent loop (Claude Code CLI).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("feature_list", help="Path to feature_list.json")
    parser.add_argument("--spec", default=None, help="Optional spec file for extra Tester context")
    parser.add_argument("--project-dir", default=None,
                        help="Project root (cwd for Tester/Worker CLI). Defaults to feature_list's parent.")
    parser.add_argument("--model", "-m", default=None,
                        help="Model for Tester & Worker (default: sonnet). E.g. sonnet, opus, haiku")
    parser.add_argument("--max-iter", type=int, default=30, help="Max iterations (default: 30)")
    parser.add_argument("--environment", "-e", default="null",
                        help="Environment name (module under environments/; default: null)")
    parser.add_argument("--env-arg", action="append", default=[],
                        help="Environment-specific kwarg, repeatable (e.g. --env-arg base_url=http://localhost)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--auto-resume", action="store_true",
                        help="After max-iter exit, exec a fresh process to continue; useful for long runs")
    parser.add_argument("--max-resumes", type=int, default=10,
                        help="Cap on --auto-resume chain (default: 10)")
    parser.add_argument("--_resume-count", type=int, default=0, help=argparse.SUPPRESS)
    args = parser.parse_args()

    level = logging.DEBUG if args.debug else logging.INFO
    utf8_stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                    errors="replace", line_buffering=True)
    handler = logging.StreamHandler(utf8_stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logging.basicConfig(level=level, handlers=[handler])
    logger = logging.getLogger("tdd_loop")

    fl_path = args.feature_list
    if not os.path.isabs(fl_path):
        fl_path = os.path.abspath(fl_path)
    if not os.path.isfile(fl_path):
        logger.error(f"Feature list not found: {fl_path}")
        sys.exit(1)

    project_dir = args.project_dir or str(Path(fl_path).resolve().parent)
    spec_file = args.spec
    if spec_file and not os.path.isabs(spec_file):
        spec_file = os.path.abspath(spec_file)

    logger.info(f"Project:      {project_dir}")
    logger.info(f"Feature list: {fl_path}")
    logger.info(f"Environment:  {args.environment}")

    try:
        from tdd_loop.orchestrator import Orchestrator
        from tdd_loop.lockfile import AutoLoopLock
    except ImportError:
        pkg_parent = str(Path(__file__).resolve().parent.parent)
        if pkg_parent not in sys.path:
            sys.path.insert(0, pkg_parent)
        from tdd_loop.orchestrator import Orchestrator
        from tdd_loop.lockfile import AutoLoopLock

    env_args = _parse_env_args(args.env_arg)
    environment = _load_environment(args.environment, env_args)

    lock_path = Path(fl_path).parent / ".tdd_loop_orchestrator.lock"
    lock = AutoLoopLock(lock_path)
    ok, msg = lock.acquire()
    if not ok:
        existing = lock.read_lock_data()
        if not existing:
            logger.error("\n" + msg)
            sys.exit(1)
        old_pid = existing.get("pid", 0)
        logger.warning(f"\nFound existing orchestrator PID={old_pid}; taking over...")
        _kill_process_tree(old_pid, logger)
        if _wait_pid_dead(old_pid, timeout=10):
            logger.info(f"  Old orchestrator PID={old_pid} is dead")
        else:
            logger.warning(f"  Old orchestrator PID={old_pid} still alive; proceeding")
        lock.force_remove()
        ok, msg = lock.acquire()
        if not ok:
            logger.error(f"\nTakeover failed:\n{msg}")
            sys.exit(1)
        logger.info("Takeover complete; lock acquired")
    else:
        logger.info(msg)

    atexit.register(lock.release)

    def _handle_signal(signum, frame):
        logger.warning(f"\nSignal {signum} received; releasing lock and exiting")
        lock.release()
        sys.exit(130)

    signal.signal(signal.SIGINT, _handle_signal)
    try:
        signal.signal(signal.SIGTERM, _handle_signal)
    except (ValueError, OSError):
        pass

    print()
    print("=" * 60)
    print("  TDD-LOOP (Tester + Worker)")
    print(f"  Model:       {args.model or '(default: sonnet)'}")
    print(f"  Environment: {args.environment}")
    print(f"  Max iters:   {args.max_iter}")
    print("=" * 60)
    print()

    orch = None
    success = False
    resume_count = args.__dict__.get("_resume_count", 0)  # noqa: argparse dest with leading underscore

    try:
        orch = Orchestrator(
            feature_list_path=fl_path,
            project_dir=project_dir,
            model=args.model,
            max_iterations=args.max_iter,
            spec_file=spec_file,
            environment=environment,
        )
        try:
            success = orch.run()
        except KeyboardInterrupt:
            logger.warning("\n[Interrupt] Ctrl+C; emitting run_end...")
            orch.emit_emergency_stop("interrupted")
            raise
        except Exception:
            logger.exception("[Crash] Orchestrator crashed")
            orch.emit_emergency_stop("crashed")
            raise
    finally:
        lock.release()

    if not success and args.auto_resume and resume_count < args.max_resumes:
        from tdd_loop.feature_list import FeatureList as _FL
        fl_check = _FL(fl_path).load()
        if fl_check.all_passed():
            sys.exit(0)
        s = fl_check.data.get("summary", {})
        pending = s.get("tests_pending", 0) + s.get("tests_failed", 0)
        if pending <= 0:
            sys.exit(0 if success else 1)
        next_count = resume_count + 1
        logger.warning(f"\n[auto-resume] Forking next run ({next_count}/{args.max_resumes})...")
        next_cmd = [sys.executable, sys.argv[0]] + sys.argv[1:]
        next_cmd = [a for a in next_cmd if not a.startswith("--_resume-count")]
        next_cmd += [f"--_resume-count={next_count}"]
        os.execv(sys.executable, next_cmd)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
