# -*- coding: utf-8 -*-
"""SWE-bench Lite mini runner.

Mirrors experiments/classeval/runner.py but for repository-level tasks. Runs
each (task, config, model) cell and writes per-task artifacts under
runs/<model>/<config>/<instance_id>/.

NOTE: This runner is the path-A "complexity-crossover" probe (10 tasks).
It is NOT a full SWE-bench Lite reproduction (300 tasks, docker harness).

Usage:
    python -m experiments.swebench_lite.runner \
        --configs baseline,tdd_loop \
        --models sonnet \
        --max-iter 25
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

_PKG_ROOT = Path(__file__).resolve().parents[2]
if str(_PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(_PKG_ROOT))

from experiments.swebench_lite import loader, to_feature_list  # noqa: E402
from experiments.swebench_lite import env_repo  # noqa: E402
from experiments.swebench_lite.evaluator import evaluate  # noqa: E402

logger = logging.getLogger("swebench_lite_runner")
RUNS_DIR = Path(__file__).resolve().parent / "runs"


def _setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def _task_dir(model: str, cfg: str, instance_id: str) -> Path:
    p = RUNS_DIR / model / cfg / instance_id
    p.mkdir(parents=True, exist_ok=True)
    return p


BASELINE_PROMPT_TEMPLATE = """\
You are working in a checked-out git repository at $TDD_REPO_DIR. A bug
report is below. Edit files in the repo to fix the bug so that the failing
test(s) pass.

## Bug report
{problem_statement}

## Failing tests that should pass after your fix
{fail_to_pass}

## Tests that should keep passing
{pass_to_pass_summary}

## Instructions
- Make the minimal set of edits needed.
- Do not modify test files (tests/ folder, test_*.py, *_test.py).
- After editing, run the failing tests with `python -m pytest -xvs <test>`.
- Do not create new files unless absolutely necessary.
"""


def run_baseline(task: dict, model: str, *, timeout: int = 1800) -> dict:
    """Single-agent baseline: Claude Code CLI gets the issue + repo dir.

    Brings up the SWEBenchRepoEnvironment, then invokes `claude -p` with
    the issue and the repo path via env vars. The agent edits files in
    place; the resulting `git diff` is the patch.
    """
    instance_id = task["instance_id"]
    env = env_repo.build(repo=task["repo"], base_commit=task["base_commit"], instance_id=instance_id)
    env.ensure()

    f2p = task["FAIL_TO_PASS"] if isinstance(task["FAIL_TO_PASS"], list) else json.loads(task["FAIL_TO_PASS"])
    p2p = task["PASS_TO_PASS"] if isinstance(task["PASS_TO_PASS"], list) else json.loads(task["PASS_TO_PASS"])

    prompt = BASELINE_PROMPT_TEMPLATE.format(
        problem_statement=task.get("problem_statement", "")[:6000],
        fail_to_pass="\n".join(f"  - {t}" for t in f2p),
        pass_to_pass_summary=f"  ({len(p2p)} other tests must continue to pass)",
    )

    import os, subprocess
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "json",
        "--tools", "default",
        "--permission-mode", "bypassPermissions",
        "--max-turns", "30",
    ]
    if model and model != "default":
        cmd.extend(["--model", model])

    env_vars = {**os.environ, **env.env_vars()}
    t0 = time.time()
    try:
        r = subprocess.run(cmd, cwd=str(env.repo_dir), capture_output=True,
                           encoding="utf-8", errors="replace", timeout=timeout, env=env_vars)
        status = "ok" if r.returncode == 0 else "error"
        stdout = r.stdout or ""
    except subprocess.TimeoutExpired:
        status, stdout = "timeout", ""

    cost = 0.0; session_id = None
    try:
        payload = json.loads(stdout) if stdout else {}
        cost = float(payload.get("total_cost_usd") or 0)
        session_id = payload.get("session_id")
    except json.JSONDecodeError:
        pass

    # capture git diff as the candidate patch
    try:
        diff = subprocess.run(["git", "-C", str(env.repo_dir), "diff"],
                              capture_output=True, text=True, timeout=30).stdout
    except Exception:
        diff = ""

    return {
        "gen_status": status,
        "gen_cost_usd": round(cost, 6),
        "gen_session_id": session_id,
        "gen_duration_s": round(time.time() - t0, 1),
        "patch": diff,
    }


def run_tdd_loop(task: dict, model: str, *, max_iter: int, variant: str = "intent_only") -> dict:
    """TDD-Loop run. Builds feature_list and invokes the orchestrator with
    the SWEBenchRepoEnvironment. Mirrors classeval/runner.run_config_tdd_loop
    in shape but plumbs through `--environment swebench_repo` and the env-args.
    """
    instance_id = task["instance_id"]
    env = env_repo.build(repo=task["repo"], base_commit=task["base_commit"], instance_id=instance_id)
    env.ensure()

    cfg_name = "tdd_loop" if variant == "intent_only" else f"tdd_loop_oracle"
    work = _task_dir(model, cfg_name, instance_id)

    fl_path = to_feature_list.build_feature_list(task, work, variant=variant)

    import os, subprocess
    cmd = [
        sys.executable, "-m", "tdd_loop.run",
        str(fl_path),
        "--project-dir", str(env.repo_dir),
        "--spec", str(work / "PROBLEM.md"),
        "--environment", "swebench_repo",
        "--env-arg", f"repo={task['repo']}",
        "--env-arg", f"base_commit={task['base_commit']}",
        "--env-arg", f"instance_id={instance_id}",
        "--max-iter", str(max_iter),
    ]
    if model and model != "default":
        cmd.extend(["--model", model])

    env_vars = {**os.environ, **env.env_vars()}
    t0 = time.time()
    try:
        r = subprocess.run(cmd, cwd=str(_PKG_ROOT), capture_output=True,
                           encoding="utf-8", errors="replace",
                           timeout=max_iter * 60 * 5, env=env_vars)
        status = "ok" if r.returncode == 0 else "error"
    except subprocess.TimeoutExpired:
        status = "timeout"

    # cost from sessions_log
    cost = 0.0; sessions = 0
    sl = work / ".tdd_loop_temp" / "sessions_log.jsonl"
    if sl.exists():
        for line in sl.read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(line)
                cost += float(rec.get("cost_usd") or 0); sessions += 1
            except json.JSONDecodeError:
                pass

    try:
        diff = subprocess.run(["git", "-C", str(env.repo_dir), "diff"],
                              capture_output=True, text=True, timeout=30).stdout
    except Exception:
        diff = ""

    return {
        "gen_status": status,
        "gen_cost_usd": round(cost, 6),
        "gen_session_count": sessions,
        "gen_duration_s": round(time.time() - t0, 1),
        "patch": diff,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--configs", default="baseline,tdd_loop",
                    help="Comma-separated configs: baseline | tdd_loop | tdd_loop_oracle")
    ap.add_argument("--models", default="sonnet")
    ap.add_argument("--max-iter", type=int, default=25)
    ap.add_argument("--n", type=int, default=10, help="Number of tasks (≤10 in mini-subset).")
    args = ap.parse_args()

    _setup_logging()
    configs = [c.strip() for c in args.configs.split(",") if c.strip()]
    models = [m.strip() for m in args.models.split(",") if m.strip()]

    tasks = loader.load_subset()[: args.n]
    logger.info("Loaded %d tasks; configs=%s; models=%s", len(tasks), configs, models)

    for task in tasks:
        for model in models:
            for cfg in configs:
                outdir = _task_dir(model, cfg, task["instance_id"])
                t0 = time.time()
                try:
                    if cfg == "baseline":
                        res = run_baseline(task, model)
                    elif cfg == "tdd_loop":
                        res = run_tdd_loop(task, model, max_iter=args.max_iter, variant="intent_only")
                    elif cfg == "tdd_loop_oracle":
                        res = run_tdd_loop(task, model, max_iter=args.max_iter, variant="oracle")
                    else:
                        raise ValueError(f"unknown config {cfg}")
                except NotImplementedError as e:
                    logger.warning("[%s/%s/%s] NOT IMPLEMENTED: %s", model, cfg, task["instance_id"], e)
                    res = {"gen_status": "not_implemented", "error": str(e)}

                # evaluate (regardless of run status, in case patch was written)
                eval_obj: dict
                try:
                    eval_obj = evaluate(env_repo.CACHE_ROOT / task["instance_id"],
                                        fail_to_pass=json.loads(task["FAIL_TO_PASS"]) if isinstance(task["FAIL_TO_PASS"], str) else task["FAIL_TO_PASS"],
                                        pass_to_pass=json.loads(task["PASS_TO_PASS"]) if isinstance(task["PASS_TO_PASS"], str) else task["PASS_TO_PASS"])
                except Exception as e:
                    eval_obj = {"ok": False, "error": str(e)}

                res.update({
                    "instance_id": task["instance_id"],
                    "config": cfg,
                    "model": model,
                    "wall_time_s": round(time.time() - t0, 1),
                    "eval": eval_obj,
                })
                (outdir / "result.json").write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
                logger.info("[%s/%s/%s] eval.instance_passed=%s wall=%.0fs",
                            model, cfg, task["instance_id"], eval_obj.get("instance_passed"), res["wall_time_s"])


if __name__ == "__main__":
    main()
