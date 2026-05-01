# -*- coding: utf-8 -*-
"""Convert a SWE-bench Lite task into a TDD-Loop feature_list.json.

Two variants:
  - intent-only: one feature per FAIL_TO_PASS test, intent text derived from
    the problem_statement and the test name (no test code embedded). This is
    the analogue of ClassEval's `tdd_loop` arm.
  - oracle: the same features, but each test_case intent embeds an instruction
    to run the actual FAIL_TO_PASS test via pytest and check exit code. This
    matches `tdd_loop_oracle` on ClassEval — the "spec quality bridge".
"""
from __future__ import annotations

import json
from pathlib import Path


def _intent_for_test(problem_statement: str, test_name: str) -> str:
    return (
        f"After applying the fix described below, the test `{test_name}` should pass. "
        f"Issue:\n{problem_statement.strip()[:1200]}"
    )


def _oracle_intent_for_test(test_name: str) -> str:
    return (
        f"ORACLE TEST RUN. Run pytest on `{test_name}` from the repo root using "
        f"`python -m pytest -xvs '{test_name}'` and verdict pass iff exit code == 0 "
        f"and pytest reports the test passed. Do not modify or short-circuit this check."
    )


def build_feature_list(task: dict, out_dir: Path, *, variant: str = "intent_only") -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    fail_to_pass = task.get("FAIL_TO_PASS") or []
    if isinstance(fail_to_pass, str):
        fail_to_pass = json.loads(fail_to_pass)

    features = []
    for i, test_name in enumerate(fail_to_pass, start=1):
        intent = (
            _oracle_intent_for_test(test_name)
            if variant == "oracle"
            else _intent_for_test(task.get("problem_statement", ""), test_name)
        )
        features.append({
            "id": f"F-{i:03d}",
            "intent": intent,
            "status": "pending",
            "dependencies": [],
            "test_cases": [
                {"id": f"T-{i:03d}-01", "intent": intent, "status": "pending"}
            ],
        })

    fl = {
        "change_name": task["instance_id"],
        "spec_dir": "PROBLEM.md",
        "features": features,
    }
    out = out_dir / "feature_list.json"
    out.write_text(json.dumps(fl, indent=2, ensure_ascii=False), encoding="utf-8")

    spec = out_dir / "PROBLEM.md"
    spec.write_text(task.get("problem_statement", ""), encoding="utf-8")
    return out
