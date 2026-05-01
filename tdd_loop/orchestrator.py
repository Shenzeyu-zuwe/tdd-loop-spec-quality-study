# -*- coding: utf-8 -*-
"""
Orchestrator — outer loop: Tester → Worker.

Exit condition: every test case in the feature list is `passed` (or `skipped`
for exceptions like repeated-failure auto-skip).

Design:
  * feature_list carries *intent only*; no test code.
  * Tester (Claude CLI, full tools) reads code, picks a verification method,
    executes, emits a JSON pass/fail verdict.
  * Worker (Claude CLI, full tools) edits source based on Tester's report.
  * An Environment adapter mediates runtime probes; Null by default.

Nothing in this file knows about any specific domain.
"""

import hashlib
import json
import logging
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    from .agent import run_agent_session
    from .client import create_client
    from .environment import Environment, NullEnvironment
    from .feature_list import FeatureList, lint_intents
except ImportError:
    _pkg_parent = str(Path(__file__).resolve().parent.parent)
    if _pkg_parent not in sys.path:
        sys.path.insert(0, _pkg_parent)
    from tdd_loop.agent import run_agent_session
    from tdd_loop.client import create_client
    from tdd_loop.environment import Environment, NullEnvironment
    from tdd_loop.feature_list import FeatureList, lint_intents

logger = logging.getLogger("tdd_loop")

# Stuck-detection thresholds.
FEATURE_SKIP_THRESHOLD = 5            # single feature exceeding this many iterations → skip
TEST_CONSECUTIVE_FAIL_THRESHOLD = 3   # per-test fail streak → auto-skip
TEST_REPEAT_REASON_THRESHOLD = 2      # same failure signature N× → auto-skip (more aggressive)

# CLI-crash backoff.
CLI_CRASH_BACKOFF_BASE = 10
CLI_CRASH_BACKOFF_MAX = 120
CLI_CRASH_ABORT_THRESHOLD = 5


def compute_session_id(feature_list_path: str) -> str:
    return hashlib.md5(os.path.abspath(feature_list_path).encode()).hexdigest()[:8]


class Orchestrator:
    """Drives Tester → Worker iterations until convergence."""

    def __init__(
        self,
        feature_list_path: str,
        project_dir: str,
        model: str | None = None,
        max_iterations: int = 30,
        spec_file: str | None = None,
        environment: Environment | None = None,
        prompts_dir: Path | None = None,
    ):
        self.project_dir = Path(project_dir)
        self.fl_path = feature_list_path
        self.max_iterations = max_iterations
        self.spec_file = spec_file

        self.client, self.model, self.backend = create_client(model)
        logger.info(f"LLM: {self.backend} / {self.model}")

        self.environment: Environment = environment or NullEnvironment()
        logger.info(f"Environment: {self.environment.name}")

        # Inject env-provided variables for all child processes (Tester & Worker).
        for k, v in (self.environment.env_vars() or {}).items():
            os.environ[k] = str(v)

        fl_dir = Path(self.fl_path).parent
        self.temp_dir = fl_dir / ".tdd_loop_temp"
        os.makedirs(self.temp_dir, exist_ok=True)
        logger.info(f"Temp dir: {self.temp_dir}")

        self._prompts_dir = prompts_dir or (Path(__file__).resolve().parent.parent / "prompts")
        self.tester_system = self._load_prompt("tester.md")
        self.worker_system = self._load_prompt("worker.md")

        self.sessions_log_path = self.temp_dir / "sessions_log.jsonl"
        self.status_json_path = self.temp_dir / "status.json"
        self.events_log_path = self.temp_dir / "events.jsonl"
        self.fl_sig_path = self.temp_dir / "feature_list.sig"

        self._check_feature_list_signature()

        self.sessions: list[dict] = self._load_existing_sessions()
        self._event_seq = self._load_existing_event_seq()
        self.iteration = 0
        self.feature_iterations: dict[str, int] = {}
        self.test_consecutive_failures: dict[str, int] = self._load_test_fail_counts()
        self.test_last_reason_sig: dict[str, str] = {}
        self.consecutive_cli_crashes = 0
        self._run_start: float | None = None

    # ── Per-test failure tracking (persisted into feature_list.json) ──

    def _load_test_fail_counts(self) -> dict[str, int]:
        counts = {}
        try:
            fl = FeatureList(self.fl_path).load()
            for f in fl.data.get("features", []):
                for t in f.get("test_cases", []):
                    fc = t.get("fail_count", 0)
                    if fc:
                        counts[t["id"]] = fc
        except Exception:
            pass
        return counts

    @staticmethod
    def _normalize_reason(reason: str) -> str:
        """Stable signature over a failure reason. Strip timestamps, coords,
        addresses, and plain numbers so 'same kind of failure' collapses to
        one signature across retries."""
        if not reason:
            return ""
        s = reason.lower()
        s = re.sub(r"\d{4}-\d{2}-\d{2}[t ]\d{2}:\d{2}:\d{2}(\.\d+)?", "<TS>", s)
        s = re.sub(r"\d{2}:\d{2}:\d{2}(\.\d+)?", "<TS>", s)
        s = re.sub(r"[\(\[]\s*-?\d+\s*,\s*-?\d+\s*[\)\]]", "<COORD>", s)
        s = re.sub(r"0x[0-9a-f]+", "<ADDR>", s)
        s = re.sub(r"\b\d+(\.\d+)?\b", "<N>", s)
        s = re.sub(r"\s+", " ", s).strip()
        return hashlib.md5(s.encode("utf-8")).hexdigest()[:16]

    def _increment_test_failure(self, fl: FeatureList, tid: str, reason: str = "") -> bool:
        """Bump per-test fail count; auto-skip when threshold hit. Returns
        True iff the test was auto-skipped this call."""
        self.test_consecutive_failures[tid] = self.test_consecutive_failures.get(tid, 0) + 1
        count = self.test_consecutive_failures[tid]

        sig = self._normalize_reason(reason)
        prev_sig = self.test_last_reason_sig.get(tid)
        repeat_hit = bool(sig and prev_sig and sig == prev_sig)
        self.test_last_reason_sig[tid] = sig

        for f in fl.data.get("features", []):
            for t in f.get("test_cases", []):
                if t["id"] == tid:
                    t["fail_count"] = count
                    t["last_reason_sig"] = sig
                    break

        if repeat_hit:
            msg = (f"Auto-skipped: same failure signature repeated "
                   f"{TEST_REPEAT_REASON_THRESHOLD}× — Tester and Worker are looping; manual review needed")
            fl.update_test(tid, "skipped", msg)
            logger.warning(f"  [AUTO-SKIP] {tid} — repeated failure signature")
            self._append_event(
                "orchestrator", "test_auto_skip",
                f"{tid} — auto-skipped (repeated reason signature)",
                test_id=tid, phase="Tester", outcome="warn",
                detail={"reason_sig": sig, "fail_count": count},
            )
            return True

        if count >= TEST_CONSECUTIVE_FAIL_THRESHOLD:
            msg = f"Auto-skipped: {count} consecutive failures (threshold={TEST_CONSECUTIVE_FAIL_THRESHOLD})"
            fl.update_test(tid, "skipped", msg)
            logger.warning(f"  [AUTO-SKIP] {tid} — {count} consecutive failures")
            self._append_event(
                "orchestrator", "test_auto_skip",
                f"{tid} — auto-skipped after {count} failures",
                test_id=tid, phase="Tester", outcome="warn",
            )
            return True
        return False

    def _reset_test_failure(self, tid: str):
        self.test_consecutive_failures.pop(tid, None)
        self.test_last_reason_sig.pop(tid, None)

    # ══════════════════════════════════════════════════════════════
    # Main loop
    # ══════════════════════════════════════════════════════════════

    def emit_emergency_stop(self, reason: str):
        """Called from signal handlers / crash paths so dashboards see a run_end."""
        try:
            fl = FeatureList(self.fl_path).load()
            elapsed = time.time() - (self._run_start or time.time())
            self._finish(fl, reason, False, elapsed)
        except Exception as e:
            logger.warning(f"  emit_emergency_stop failed: {e}")

    def _finish(self, fl: FeatureList, reason: str, success: bool, total_elapsed: float):
        s = fl.data.get("summary", {})
        self._append_event(
            "orchestrator", "run_end",
            f"Loop ended: {reason} ({s.get('tests_passed', 0)}/{s.get('total_tests', 0)} tests passed)",
            phase="done", outcome="ok" if success else "warn",
            detail={
                "reason": reason,
                "iterations": self.iteration,
                "elapsed_seconds": round(total_elapsed, 1),
                "summary": s,
            },
        )
        self._write_status(fl, running=False, current_phase=("done" if success else f"stopped:{reason}"))
        try:
            self._write_report(fl, total_elapsed, "ALL PASSED" if success else reason.upper())
        except Exception as e:
            logger.warning(f"  _write_report failed: {e}")
        try:
            self.environment.shutdown()
        except Exception as e:
            logger.warning(f"  environment.shutdown failed: {e}")

    def run(self) -> bool:
        run_start = time.time()
        fl = FeatureList(self.fl_path).load()
        logger.info(f"\n{fl.get_progress_report()}")
        self._reset_events_log()

        # Intent-anchor lint.
        lint_warnings = lint_intents(fl.data, extra_anchors=self.environment.anchor_patterns)
        if lint_warnings:
            logger.warning(f"\n[Intent Linter] {len(lint_warnings)} intents missing verification anchors:")
            for w in lint_warnings[:10]:
                logger.warning(f"  - {w['id']}: {w['intent'][:80]}")
            self._append_event(
                "orchestrator", "intent_lint",
                f"{len(lint_warnings)} intents missing anchors",
                phase="setup", outcome="warn",
                detail={"warnings": lint_warnings[:50]},
            )

        # Bring environment up.
        logger.info(f"\n[Setup] Ensuring environment '{self.environment.name}'...")
        env_ready = False
        try:
            env_ready = bool(self.environment.ensure())
        except Exception as e:
            logger.error(f"  environment.ensure() crashed: {e}")
        self._append_event(
            "orchestrator", "env_ready",
            f"Environment ready" if env_ready else "Environment not ready",
            phase="setup", outcome="ok" if env_ready else "fail",
            detail={"env": self.environment.describe()},
        )
        if not env_ready:
            logger.warning("\n⚠️  Environment unavailable; runtime-requiring tests will report test_env_error.")

        self._run_start = time.time()

        total_features = len(fl.data.get("features", []))
        total_tests = sum(len(f.get("test_cases", [])) for f in fl.data.get("features", []))
        logger.info(f"\n🚀 TDD Loop starting: {total_features} features, {total_tests} tests, max {self.max_iterations} iterations")
        self._append_event(
            "orchestrator", "loop_ready",
            f"{total_features} features, {total_tests} tests, max_iter={self.max_iterations}",
            phase="loop", outcome="ok", detail={"model": self.model},
        )
        self._write_status(fl, running=True)

        # Startup regression check if everything is already green.
        if fl.all_passed():
            logger.info("\n[Startup] All features already passed, running regression check...")
            if self._regression_check(fl):
                total_elapsed = time.time() - run_start
                logger.info(f"\nALL FEATURES PASSED (0 iterations, {self._format_elapsed(total_elapsed)})")
                self._finish(fl, "all_passed", True, total_elapsed)
                return True
            logger.warning("  Regression detected, entering main loop to fix...")
            fl.save()

        # ── Main iteration loop ─────────────────────────────────────
        while self.iteration < self.max_iterations:
            self.iteration += 1
            iter_start = time.time()
            total_elapsed = time.time() - run_start

            logger.info(f"\n{'=' * 60}")
            logger.info(f"ITERATION {self.iteration}/{self.max_iterations}  (total: {self._format_elapsed(total_elapsed)})")
            logger.info(f"{'=' * 60}")
            self._log_progress_bar(fl)

            # Pre-iteration env health check.
            try:
                env_ok = self.environment.health_check()
            except Exception as e:
                logger.error(f"  environment.health_check() crashed: {e}")
                env_ok = False
            if not env_ok:
                logger.error("  Environment unhealthy; cannot proceed")
                self._append_event("orchestrator", "env_health", "unhealthy", phase="loop", outcome="fail")
                break

            feature = fl.get_next_feature()
            if not feature:
                logger.warning("No actionable features remaining")
                break

            fid = feature["id"]
            self.feature_iterations[fid] = self.feature_iterations.get(fid, 0) + 1
            feat_iter = self.feature_iterations[fid]

            logger.info(f"\n>> Feature: {fid} {feature['intent'][:60]} (attempt {feat_iter})")

            if feat_iter > FEATURE_SKIP_THRESHOLD:
                logger.warning(f"  [SKIP] {fid} tried {FEATURE_SKIP_THRESHOLD}×, manual fix needed")
                fl.update_feature_status(fid, "skipped")
                fl.save()
                continue

            # ── Phase 1: Tester ────────────────────────────────────
            logger.info(f"\n[Phase 1/2] Tester verifying {fid}...")
            self._write_status(fl, current_feature=fid, current_phase="Tester")
            phase_start = time.time()

            all_passed = True
            short_circuit = False
            for test in feature.get("test_cases", []):
                if test["status"] in ("passed", "skipped"):
                    continue
                tid = test["id"]
                logger.info(f"  Testing {tid}: {test['intent'][:80]}")
                self._write_status(fl, current_feature=fid, current_phase="Tester",
                                   current_test=tid, current_test_intent=test["intent"])

                try:
                    self.environment.notify_pre_verify(fid, tid)
                except Exception as e:
                    logger.warning(f"  environment.notify_pre_verify crashed: {e}")

                result = self._tester_verify(fl, feature, test)
                if result is None:
                    all_passed = False
                    break

                if result.get("passed"):
                    fl.update_test(tid, "passed", result.get("reason", ""))
                    self._reset_test_failure(tid)
                    logger.info(f"  [PASS] {tid}")
                    self._append_event("tester", "test_result", f"{tid} — PASS",
                                       feature_id=fid, test_id=tid, phase="Tester", outcome="ok")
                elif result.get("failure_type") == "test_env_error":
                    logger.warning(f"  [ENV_ERROR] {tid}: {result.get('reason', '')[:100]}")
                    self._append_event("tester", "test_env_error", f"{tid} — env error",
                                       feature_id=fid, test_id=tid, phase="Tester", outcome="warn")
                    all_passed = False
                else:
                    fl.update_test(tid, "failed", result.get("reason", ""))
                    logger.info(f"  [FAIL] {tid}: {result.get('reason', '')[:100]}")
                    self._append_event("tester", "test_result",
                                       f"{tid} — FAIL: {result.get('reason', '')[:80]}",
                                       feature_id=fid, test_id=tid, phase="Tester", outcome="fail",
                                       detail={"failure_type": result.get("failure_type"),
                                               "details": result.get("details", "")[:500]})
                    self._increment_test_failure(fl, tid, result.get("reason", ""))
                    all_passed = False
                    if result.get("failure_type") == "not_implemented":
                        logger.info(f"  [SHORT-CIRCUIT] {fid} not implemented → Worker")
                        short_circuit = True
                        break

            fl.save()
            logger.info(f"  Tester done ({self._format_elapsed(time.time() - phase_start)})")

            feature = fl.get_feature(fid)
            if feature["status"] == "passed":
                self.iteration -= 1  # a no-op iteration; don't charge it
                logger.info(f"  [PASS] {fid} all tests passed")
                if fl.all_passed():
                    if not self._regression_check(fl):
                        logger.warning("  Regression detected; continuing loop")
                        fl.save()
                        continue
                    total_elapsed = time.time() - run_start
                    logger.info(f"\nALL FEATURES PASSED ({self.iteration} iters, {self._format_elapsed(total_elapsed)})")
                    self._finish(fl, "all_passed", True, total_elapsed)
                    return True
                continue

            # ── Phase 2: Worker ────────────────────────────────────
            failed_tests = fl.get_failed_tests(fid)
            if not failed_tests:
                logger.info("  No failed tests to fix, skipping Worker")
                continue

            logger.info(f"\n[Phase 2/2] Worker fixing {fid} ({len(failed_tests)} failed)...")
            self._write_status(fl, current_feature=fid, current_phase="Worker")
            phase_start = time.time()
            modified = self._worker_fix(fl, feature, failed_tests)
            logger.info(f"  Worker done ({self._format_elapsed(time.time() - phase_start)})")

            try:
                self.environment.notify_post_worker(modified)
            except Exception as e:
                logger.warning(f"  environment.notify_post_worker crashed: {e}")

            self._log_sessions_dashboard()
            self._write_status(fl, current_phase="idle")

            if fl.all_passed():
                total_elapsed = time.time() - run_start
                logger.info(f"\nALL FEATURES PASSED ({self.iteration} iters, {self._format_elapsed(total_elapsed)})")
                self._finish(fl, "all_passed", True, total_elapsed)
                return True

            logger.info(f"\n{fl.get_progress_report()}")
            time.sleep(1)

        total_elapsed = time.time() - run_start
        logger.warning(f"\nMax iterations reached ({self.max_iterations}), {self._format_elapsed(total_elapsed)}")
        self._finish(fl, "max_iterations_reached", False, total_elapsed)
        return False

    # ══════════════════════════════════════════════════════════════
    # Resume-header (one-line identity card for `claude --resume` listings)
    # ══════════════════════════════════════════════════════════════

    def _build_resume_header(self, fl: FeatureList, role: str, subject: str,
                              action: str, intent: str) -> str:
        change_name = fl.data.get("change_name", "unknown")
        snippet = (intent or "").strip().replace("\n", " ")
        if len(snippet) > 60:
            snippet = snippet[:60] + "…"
        return (
            f"TDDLoop {change_name} [{role}] · {subject} · iter-{self.iteration} · {action}\n"
            f"  ↳ {snippet}"
        )

    # ══════════════════════════════════════════════════════════════
    # Phase 1: Tester
    # ══════════════════════════════════════════════════════════════

    def _tester_verify(self, fl: FeatureList, feature: dict, test: dict,
                        action: str = "verify") -> dict | None:
        spec_context = self._get_spec_context()
        harness = self.environment.capabilities or "(no runtime harness)"

        user_msg = (
            f"## Target intent\n{test['intent']}\n\n"
            f"## Feature context\n{feature['intent']}\n\n"
            f"## Verification Harness\n{harness}\n\n"
            f"{spec_context}"
            f"Verify the target intent and emit the JSON verdict."
        )

        resume_header = self._build_resume_header(
            fl, role="Tester",
            subject=f"{feature['id']}/{test['id']}",
            action=action, intent=test["intent"],
        )

        started = datetime.now().isoformat()
        status, text, meta = run_agent_session(
            self.client, self.model,
            system_prompt=self.tester_system,
            user_message=user_msg,
            project_dir=self.project_dir,
            use_tools=True, json_mode=True,
            max_turns=30, resume_header=resume_header,
        )
        self._record_session("Tester", feature["id"], f"verify {test['id']}", status, meta,
                             started_at=started, test_id=test["id"], prompt=user_msg)

        if status != "ok":
            logger.error(f"  Tester session failed: {status}")
            self.consecutive_cli_crashes += 1
            fl.update_test(test["id"], "failed", f"Tester CLI crash (status={status})")
            self._increment_test_failure(fl, test["id"], f"Tester CLI crash (status={status})")
            fl.save()
            if self.consecutive_cli_crashes >= CLI_CRASH_ABORT_THRESHOLD:
                logger.error(f"  {self.consecutive_cli_crashes} consecutive CLI crashes, aborting")
                return None
            backoff = min(CLI_CRASH_BACKOFF_BASE * (2 ** (self.consecutive_cli_crashes - 1)),
                          CLI_CRASH_BACKOFF_MAX)
            logger.info(f"  Waiting {backoff}s before retry...")
            time.sleep(backoff)
            return None

        self.consecutive_cli_crashes = 0

        try:
            result = json.loads(text)
            if isinstance(result, dict) and "passed" in result:
                return result
        except (json.JSONDecodeError, TypeError):
            pass

        result = self._extract_json_from_text(text)
        if result:
            return result

        logger.warning(f"  Tester output not JSON-parseable: {(text or '')[:200]}")
        return {"passed": False, "reason": "Tester output not parseable",
                "failure_type": "test_env_error", "details": ""}

    # ══════════════════════════════════════════════════════════════
    # Phase 2: Worker
    # ══════════════════════════════════════════════════════════════

    def _worker_fix(self, fl: FeatureList, feature: dict, failed_tests: list[dict]) -> list[str]:
        test_reports = [
            {"test_id": t["id"], "intent": t["intent"], "failure_reason": t.get("reason", "")}
            for t in failed_tests
        ]
        spec_context = self._get_spec_context()
        user_msg = (
            f"## Feature: {feature['id']}\n{feature['intent']}\n\n"
            f"## Failed tests\n{json.dumps(test_reports, ensure_ascii=False, indent=2)}\n\n"
            f"{spec_context}"
            f"Edit source code so these tests pass. Do not write test code; do not verify."
        )

        fl.update_feature_status(feature["id"], "in_progress")
        fl.save()

        self._append_event("worker", "fix_begin",
                           f"Worker fixing {feature['id']} ({len(failed_tests)} failed)",
                           feature_id=feature["id"], phase="Worker", outcome="pending")

        resume_header = self._build_resume_header(
            fl, role="Worker", subject=feature["id"],
            action=f"fix {len(failed_tests)} tests", intent=feature["intent"],
        )

        started = datetime.now().isoformat()
        pre_added, pre_deleted = self._get_diff_stats()
        status, text, meta = run_agent_session(
            self.client, self.model,
            system_prompt=self.worker_system,
            user_message=user_msg,
            project_dir=self.project_dir,
            use_tools=True, json_mode=False,
            max_turns=30, resume_header=resume_header,
        )
        post_added, post_deleted = self._get_diff_stats()
        lines_added = max(0, post_added - pre_added)
        lines_deleted = max(0, post_deleted - pre_deleted)
        test_ids = [t["id"] for t in failed_tests]

        self._record_session("Worker", feature["id"], f"fix {len(failed_tests)} tests",
                             status, meta, started_at=started, test_id=",".join(test_ids),
                             prompt=user_msg, lines_added=lines_added, lines_deleted=lines_deleted)

        if status == "ok":
            logger.info(f"  ✓ Worker done (+{lines_added}/-{lines_deleted})")
        else:
            logger.warning(f"  ✗ Worker failed (exit={status})")
            for t in failed_tests:
                self._increment_test_failure(fl, t["id"], f"Worker crash (exit={status})")
            fl.save()

        self._append_event("worker", "fix_done", f"Worker done: {status}",
                           feature_id=feature["id"], phase="Worker",
                           outcome="ok" if status == "ok" else "fail",
                           detail={"session_id": meta.get("session_id")})

        return self._detect_changes()

    # ══════════════════════════════════════════════════════════════
    # Regression pass
    # ══════════════════════════════════════════════════════════════

    def _regression_check(self, fl: FeatureList) -> bool:
        """After full green, re-run every test to catch regressions introduced
        while fixing later features. Returns True iff still all-green."""
        all_tests = [(f, t) for f in fl.data.get("features", []) for t in f.get("test_cases", [])]
        if not all_tests:
            return True

        logger.info(f"\n[Regression] Re-running {len(all_tests)} test cases...")
        self._write_status(fl, current_phase="Regression")
        self._append_event("orchestrator", "regression_start",
                           f"Regression over {len(all_tests)} tests",
                           phase="Regression", outcome="pending")

        regressed = False
        for feature, test in all_tests:
            tid, fid = test["id"], feature["id"]
            logger.info(f"  [Regression] {tid}: {test['intent'][:60]}")
            self._write_status(fl, current_feature=fid, current_phase="Regression",
                               current_test=tid, current_test_intent=test["intent"])
            result = self._tester_verify(fl, feature, test, action="regression")
            if result is None:
                # Infra problem, not a regression. One retry, then skip.
                logger.warning(f"  [Regression] {tid} — CLI crash, retrying...")
                fl.update_test(tid, "passed", "Regression retry in progress")
                result = self._tester_verify(fl, feature, test, action="regression-retry")
                if result is None:
                    fl.update_test(tid, "passed", "Regression skipped: CLI crash twice")
                    self._append_event("tester", "regression_skip", f"{tid} — infra skip",
                                       feature_id=fid, test_id=tid, phase="Regression", outcome="ok")
                    continue
            if result.get("passed"):
                if test.get("status") != "passed":
                    fl.update_test(tid, "passed", f"Regression passed: {result.get('reason', '')}")
                self.test_consecutive_failures.pop(tid, None)
                self.test_last_reason_sig.pop(tid, None)
                for f_ in fl.data.get("features", []):
                    for t_ in f_.get("test_cases", []):
                        if t_["id"] == tid:
                            t_.pop("fail_count", None)
                            t_.pop("last_reason_sig", None)
                            break
                fl.save()
                self._append_event("tester", "regression_ok", f"{tid} — regression OK",
                                   feature_id=fid, test_id=tid, phase="Regression", outcome="ok")
            else:
                logger.warning(f"  [Regression] {tid} — REGRESSED: {result.get('reason', '')[:80]}")
                fl.update_test(tid, "failed", f"Regression: {result.get('reason', '')}")
                self._append_event("tester", "regression_fail", f"{tid} — REGRESSED",
                                   feature_id=fid, test_id=tid, phase="Regression", outcome="fail")
                regressed = True

        self._append_event("orchestrator", "regression_done",
                           "no regressions" if not regressed else "regressions found",
                           phase="Regression", outcome="ok" if not regressed else "fail")
        return not regressed

    # ══════════════════════════════════════════════════════════════
    # Report writer
    # ══════════════════════════════════════════════════════════════

    def _write_report(self, fl: FeatureList, total_elapsed: float, result: str):
        summary = fl.data.get("summary", {})
        total_cost = sum(s.get("cost_usd", 0) for s in self.sessions)
        now = datetime.now()
        start_time = (datetime.fromtimestamp(self._run_start).strftime("%Y-%m-%d %H:%M:%S")
                      if self._run_start else now.strftime("%Y-%m-%d %H:%M:%S"))
        end_time = now.strftime("%Y-%m-%d %H:%M:%S")

        lines = [
            f"# TDDLoop Report\n",
            f"| | |", f"|---|---|",
            f"| Result | **{result}** |",
            f"| Change | {fl.data.get('change_name', '')} |",
            f"| Environment | {self.environment.name} |",
            f"| Start | {start_time} |",
            f"| End | {end_time} |",
            f"| Duration | {self._format_elapsed(total_elapsed)} |",
            f"| Iterations | {self.iteration} |",
            f"| Model | {self.model} |",
            f"| Cost | ${total_cost:.4f} |",
            f"| Sessions | {len(self.sessions)} |",
            "",
            f"## Features ({summary.get('passed', 0)}/{summary.get('total_features', 0)} passed)",
            "",
        ]
        for f in fl.data.get("features", []):
            fstatus = f["status"].upper()
            lines.append(f"### [{fstatus}] {f['id']} {f['intent']}\n")
            for t in f.get("test_cases", []):
                tstatus = t["status"].upper()
                icon = "✓" if tstatus == "PASSED" else "✗" if tstatus == "FAILED" else "-"
                lines.append(f"- [{icon}] **{t['id']}** {t['intent']}")
                if t.get("reason"):
                    lines.append(f"  - {t['reason'][:200]}")
            lines.append("")

        lines.append(f"## Sessions ({len(self.sessions)} total, ${total_cost:.4f})\n")
        lines.append(f"| # | Role | Feature | Task | Status | Duration | Cost | Session ID |")
        lines.append(f"|---|------|---------|------|--------|----------|------|------------|")
        for i, s in enumerate(self.sessions):
            dur_s = s.get("duration_ms", 0) / 1000
            dur_str = f"{dur_s:.0f}s" if dur_s < 60 else f"{int(dur_s)//60}m{int(dur_s)%60}s"
            sid = (s.get("session_id") or "")[:12]
            lines.append(
                f"| {i+1} | {s['role']} | {s['feature_id']} | {s['task'][:40]} | "
                f"{s['status']} | {dur_str} | ${s.get('cost_usd', 0):.4f} | {sid}.. |"
            )

        report_path = Path(self.temp_dir) / "report.md"
        try:
            report_path.write_text("\n".join(lines), encoding="utf-8")
            logger.info(f"  Report: {report_path}")
        except OSError as e:
            logger.warning(f"  Failed to write report: {e}")

    # ══════════════════════════════════════════════════════════════
    # Spec & diff helpers
    # ══════════════════════════════════════════════════════════════

    def _get_spec_context(self) -> str:
        if not self.spec_file:
            return ""
        try:
            content = Path(self.spec_file).read_text(encoding="utf-8")
            return f"## Spec\n{content}\n\n"
        except OSError:
            return ""

    def _detect_changes(self) -> list[str]:
        try:
            r = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                cwd=str(self.project_dir),
                capture_output=True, encoding="utf-8", timeout=10,
            )
            return [f for f in (r.stdout or "").strip().split("\n") if f]
        except Exception:
            return []

    def _get_diff_stats(self) -> tuple[int, int]:
        try:
            r = subprocess.run(
                ["git", "diff", "--numstat"],
                cwd=str(self.project_dir),
                capture_output=True, text=True, timeout=10,
            )
            added = deleted = 0
            for line in (r.stdout or "").strip().split("\n"):
                parts = line.split("\t")
                if len(parts) >= 2 and parts[0] != "-":
                    try:
                        added += int(parts[0])
                        deleted += int(parts[1])
                    except ValueError:
                        pass
            return added, deleted
        except Exception:
            return 0, 0

    # ══════════════════════════════════════════════════════════════
    # JSON extraction
    # ══════════════════════════════════════════════════════════════

    def _extract_json_from_text(self, text: str) -> dict | None:
        if not text:
            return None
        m = re.search(r'```(?:json)?\s*\n(.*?)\n```', text, re.DOTALL)
        if m:
            try:
                result = json.loads(m.group(1))
                if isinstance(result, dict) and "passed" in result:
                    return result
            except json.JSONDecodeError:
                pass
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("{"):
                try:
                    result = json.loads(line)
                    if isinstance(result, dict) and "passed" in result:
                        return result
                except json.JSONDecodeError:
                    continue
        return None

    # ══════════════════════════════════════════════════════════════
    # Logs, status, persistence
    # ══════════════════════════════════════════════════════════════

    def _load_prompt(self, name: str) -> str:
        path = self._prompts_dir / name
        return path.read_text(encoding="utf-8")

    def _format_elapsed(self, seconds: float) -> str:
        if seconds < 60:
            return f"{seconds:.1f}s"
        m, s = divmod(int(seconds), 60)
        return f"{m}m{s}s"

    def _log_progress_bar(self, fl: FeatureList):
        s = fl.data.get("summary", {})
        total = s.get("total_tests", 0)
        if total == 0:
            return
        passed, failed = s.get("tests_passed", 0), s.get("tests_failed", 0)
        pending, skipped = s.get("tests_pending", 0), s.get("tests_skipped", 0)
        bar_len = 30
        p_bar = int(bar_len * passed / total)
        f_bar = int(bar_len * failed / total)
        s_bar = int(bar_len * skipped / total)
        rest = bar_len - p_bar - f_bar - s_bar
        bar = "█" * p_bar + "▓" * f_bar + "░" * s_bar + "·" * rest
        pct = int(100 * passed / total)
        logger.info(f"  Progress: [{bar}] {pct}% ({passed}/{total} passed, {failed} failed, {pending} pending, {skipped} skipped)")

    def _check_feature_list_signature(self):
        """If the feature list's intent set changed since last run, wipe the
        logs so dashboards don't conflate two different specs."""
        cur_sig = FeatureList(self.fl_path).load().signature()
        if not cur_sig:
            return
        prev_sig = ""
        if self.fl_sig_path.exists():
            try:
                prev_sig = self.fl_sig_path.read_text(encoding="utf-8").strip()
            except OSError:
                prev_sig = ""
        if prev_sig == cur_sig:
            return
        if not prev_sig:
            try:
                self.fl_sig_path.write_text(cur_sig, encoding="utf-8")
            except OSError as e:
                logger.warning(f"  Failed to write feature_list.sig: {e}")
            return
        # Signature changed — clear history.
        for p in (self.sessions_log_path, self.events_log_path):
            if p.exists():
                try:
                    p.unlink()
                except OSError as e:
                    logger.warning(f"  Failed to clear {p.name}: {e}")
        try:
            self.fl_sig_path.write_text(cur_sig, encoding="utf-8")
        except OSError:
            pass
        logger.info("  Feature list signature changed; history cleared")

    def _load_existing_sessions(self) -> list[dict]:
        sessions = []
        if self.sessions_log_path.exists():
            try:
                for line in self.sessions_log_path.read_text(encoding="utf-8").strip().split("\n"):
                    if line.strip():
                        try:
                            sessions.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
            except OSError:
                pass
        return sessions

    def _load_existing_event_seq(self) -> int:
        max_seq = 0
        if self.events_log_path.exists():
            try:
                for line in self.events_log_path.read_text(encoding="utf-8").strip().split("\n"):
                    if line.strip():
                        try:
                            rec = json.loads(line)
                            max_seq = max(max_seq, rec.get("seq", 0))
                        except json.JSONDecodeError:
                            pass
            except OSError:
                pass
        return max_seq

    def _reset_events_log(self):
        self._event_seq += 1
        try:
            rec = {
                "seq": self._event_seq, "ts": datetime.now().isoformat(), "iteration": 0,
                "actor": "orchestrator", "kind": "run_start", "phase": "setup",
                "feature_id": "", "test_id": "",
                "summary": "TDD loop restarted" if self._event_seq > 1 else "TDD loop started",
                "outcome": "ok", "detail": {}, "parent_seq": None,
            }
            with open(self.events_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        except OSError as e:
            logger.warning(f"  Failed to append events.jsonl: {e}")

    def _append_event(self, actor, kind, summary, *, phase="", feature_id="",
                       test_id="", outcome="", detail=None, parent_seq=None):
        self._event_seq += 1
        rec = {
            "seq": self._event_seq, "ts": datetime.now().isoformat(),
            "iteration": self.iteration, "actor": actor, "kind": kind,
            "phase": phase, "feature_id": feature_id, "test_id": test_id,
            "summary": (summary or "")[:800], "outcome": outcome,
            "detail": detail if detail is not None else {},
            "parent_seq": parent_seq,
        }
        try:
            with open(self.events_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        except OSError:
            pass

    def _record_session(self, role, feature_id, task_desc, status, meta,
                         started_at="", test_id="", prompt="",
                         lines_added=0, lines_deleted=0):
        finished_at = datetime.now().isoformat()
        record = {
            "iteration": self.iteration,
            "started_at": started_at or finished_at,
            "finished_at": finished_at,
            "role": role, "feature_id": feature_id, "test_id": test_id,
            "task": task_desc[:120], "status": status,
            "session_id": meta.get("session_id"),
            "cost_usd": meta.get("cost_usd", 0),
            "duration_ms": meta.get("duration_ms", 0),
            "num_turns": meta.get("num_turns", 0),
            "prompt": prompt[:2000],
            "lines_added": lines_added, "lines_deleted": lines_deleted,
        }
        self.sessions.append(record)
        try:
            with open(self.sessions_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except OSError:
            pass

    def _log_sessions_dashboard(self):
        if not self.sessions:
            return
        total_cost = sum(s.get("cost_usd", 0) for s in self.sessions)
        logger.info(f"\n── Sessions ({len(self.sessions)} total, ${total_cost:.4f}) ──")
        for i, s in enumerate(self.sessions[-10:]):  # last 10 only
            sid = (s.get("session_id") or "N/A")[:12]
            dur_s = s.get("duration_ms", 0) / 1000
            dur_str = f"{dur_s:.0f}s" if dur_s < 60 else f"{int(dur_s)//60}m{int(dur_s)%60}s"
            logger.info(
                f"  {i+1:>3} {s['role']:8} {s['feature_id']:10} {s['status']:5} "
                f"{dur_str:>7} ${s.get('cost_usd', 0):.4f} {sid:14} {s['task'][:40]}"
            )

    def _write_status(self, fl: FeatureList, running: bool = True,
                       current_feature: str = "", current_phase: str = "",
                       current_test: str = "", current_test_intent: str = ""):
        elapsed = time.time() - self._run_start if self._run_start else 0
        summary = fl.data.get("summary", {})
        features_status = []
        for f in fl.data.get("features", []):
            tests = [{"id": t["id"], "intent": t["intent"][:80], "status": t["status"],
                       "reason": (t.get("reason") or "")[:200]}
                      for t in f.get("test_cases", [])]
            features_status.append({"id": f["id"], "intent": f["intent"][:80],
                                     "status": f["status"], "test_cases": tests})
        status = {
            "running": running,
            "iteration": self.iteration,
            "max_iterations": self.max_iterations,
            "elapsed_seconds": round(elapsed, 1),
            "current_feature": current_feature,
            "current_phase": current_phase,
            "current_test": current_test,
            "current_test_intent": current_test_intent[:100],
            "model": self.model,
            "environment": self.environment.describe(),
            "summary": summary,
            "features": features_status,
            "sessions": self.sessions,
            "total_cost_usd": round(sum(s.get("cost_usd", 0) for s in self.sessions), 6),
            "updated_at": datetime.now().isoformat(),
        }
        try:
            with open(self.status_json_path, "w", encoding="utf-8") as f:
                json.dump(status, f, ensure_ascii=False, indent=2)
        except OSError:
            pass
