# -*- coding: utf-8 -*-
"""SWE-bench Lite evaluator (docker-less fallback).

A run "passes" iff after the candidate's edits:
  - every test in FAIL_TO_PASS now passes
  - every test in PASS_TO_PASS still passes

For canonical SWE-bench Lite numbers, swap this for the official
`swebench.harness.run_evaluation` invocation. We deliberately do not
duplicate the official harness's retry/cleanup logic here.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _run_pytest(repo_dir: Path, test_ids: list[str], timeout: int = 600) -> dict:
    if not test_ids:
        return {"passed": [], "failed": [], "errored": [], "n": 0}
    cmd = [sys.executable, "-m", "pytest", "-x", "--no-header", "-q", *test_ids]
    try:
        cp = subprocess.run(cmd, cwd=repo_dir, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"passed": [], "failed": test_ids, "errored": [], "n": len(test_ids), "timeout": True}

    out = (cp.stdout or "") + "\n" + (cp.stderr or "")
    passed, failed, errored = [], [], []
    for tid in test_ids:
        if f"{tid} PASSED" in out or f"{tid}::passed" in out:
            passed.append(tid)
        elif f"{tid} FAILED" in out or " FAILED " in out and tid in out:
            failed.append(tid)
        elif f"{tid} ERROR" in out:
            errored.append(tid)
        else:
            # Conservative: if pytest exit code is 0, assume pass
            (passed if cp.returncode == 0 else failed).append(tid)
    return {"passed": passed, "failed": failed, "errored": errored, "n": len(test_ids), "raw": out[-2000:]}


def evaluate(repo_dir: Path, fail_to_pass: list[str], pass_to_pass: list[str]) -> dict:
    f2p = _run_pytest(repo_dir, fail_to_pass)
    p2p = _run_pytest(repo_dir, pass_to_pass)
    ok = (len(f2p["passed"]) == f2p["n"]) and (len(p2p["passed"]) == p2p["n"])
    return {
        "ok": True,
        "instance_passed": ok,
        "fail_to_pass": f2p,
        "pass_to_pass": p2p,
    }
