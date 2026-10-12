# -*- coding: utf-8 -*-
"""Failure-mode classifier for tdd_loop runs.

Reads each tdd_loop and tdd_loop_oracle failed task and assigns one label
per task plus a per-method breakdown when the task has mixed signals.

Taxonomy:
  F1 Tester false-reject   — feature skipped/failed but method passes held-out test
  F2 Tester false-accept   — all features marked passed but method fails held-out test
  F3 Worker could-not-fix  — feature skipped/failed AND method fails held-out test
  F5 Other Env/CLI failure — gen_status in {error, timeout, crashed}, without F6 pattern
  F6 Late Env/CLI failure with mixed feature states — non-ok exit with
                               iters >= LATE_CLI_MIN_ITERS and a mix of passed/skipped features
  F0 Mixed                 — task contains both F1 and F3 signals; reported with breakdown
  F4                       — unused in this release (historical placeholder)

The mapping between feature[i] and method/test class is based on extracting
the method name from each feature's intent and matching against the keys of
result.eval.method_results (which follow the pattern <ClassName>Test<MethodName>).

LATE_CLI_MIN_ITERS is a *retrospective analysis* constant (fixed before generating
the labels reported in the paper; not a runtime knob of the factorial runs).
It is distinct from orchestrator safeguards (FEATURE_SKIP_THRESHOLD=5, etc.) and
max_iterations=20. Chosen as 7 ≈ just above FEATURE_SKIP_THRESHOLD so that a
skip/pass mix is plausible.
"""
from __future__ import annotations

import glob
import json
import re
from collections import Counter
from pathlib import Path

RUNS = Path("E:/AICoding/Paper/experiments/classeval/runs")
METHOD_RX = re.compile(r"`([A-Za-z_][A-Za-z0-9_]*)\(")  # extracts `name(` -> name

# Retrospective analysis constant (not an orchestrator runtime knob).
LATE_CLI_MIN_ITERS = 7


def _read_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        try:
            return json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            return None


def _method_from_intent(intent: str) -> str | None:
    m = METHOD_RX.search(intent or "")
    return m.group(1) if m else None


def _normalize(name: str) -> str:
    return (name or "").lower().replace("_", "")


def _match_method_passed(method_name: str, method_results: dict) -> bool | None:
    """Return whether the method's held-out test class passed.
    method_results keys look like 'BigNumCalculatorTestAdd' for method 'add'.
    """
    target = _normalize(method_name)
    for k, v in method_results.items():
        # split on 'Test' to grab the method-name suffix
        parts = k.split("Test", 1)
        if len(parts) == 2 and _normalize(parts[1]) == target:
            return bool(v.get("passed"))
    # fallback: substring match
    for k, v in method_results.items():
        if target and target in _normalize(k):
            return bool(v.get("passed"))
    return None


def classify_task(task_dir: Path) -> dict:
    rj = _read_json(task_dir / "result.json")
    fj = _read_json(task_dir / "feature_list.json")
    if rj is None:
        return {"task_id": task_dir.name, "label": "missing", "detail": "no result.json"}

    eval_obj = rj.get("eval") or {}
    class_passed = eval_obj.get("class_passed")
    method_results = eval_obj.get("method_results") or {}
    gen_status = rj.get("gen_status")
    iters = rj.get("gen_iterations")

    record = {
        "task_id": rj.get("task_id"),
        "model": rj.get("model"),
        "config": rj.get("config"),
        "gen_status": gen_status,
        "gen_iterations": iters,
        "gen_session_count": rj.get("gen_session_count"),
        "class_passed": class_passed,
        "method_pass_count": eval_obj.get("method_pass_count"),
        "method_total": eval_obj.get("method_total"),
    }

    if class_passed:
        record["label"] = "PASS"
        return record

    # Env/CLI non-ok status: F6 = late + mixed feature progress; F5 = other.
    if gen_status in ("error", "timeout", "crashed"):
        feats = (fj or {}).get("features") or []
        skipped = sum(1 for f in feats if f.get("status") in ("skipped", "failed"))
        passed = sum(1 for f in feats if f.get("status") == "passed")
        if skipped and passed and (iters or 0) >= LATE_CLI_MIN_ITERS:
            record["label"] = "F6"
        else:
            record["label"] = "F5"
        record["detail"] = (
            f"gen_status={gen_status} feats(passed={passed},skipped={skipped})"
            f" iters={iters} min_iters={LATE_CLI_MIN_ITERS}"
        )
        return record

    feats = (fj or {}).get("features") or []
    if not feats:
        record["label"] = "unknown"
        record["detail"] = "no feature_list features"
        return record

    feat_statuses = [f.get("status") for f in feats]
    all_features_passed = all(s == "passed" for s in feat_statuses)

    if all_features_passed:
        # Loop terminated declaring full green; held-out unittest disagrees.
        record["label"] = "F2"
        record["detail"] = f"all {len(feats)} features marked passed; methods passed {eval_obj.get('method_pass_count')}/{eval_obj.get('method_total')}"
        return record

    # Some features skipped/failed — split per feature into F1 vs F3
    f1_count = 0  # Tester false-reject (feature failed, method passes held-out)
    f3_count = 0  # Worker could-not-fix (feature failed, method also fails held-out)
    unknown = 0
    per_method = []
    for f in feats:
        status = f.get("status")
        if status == "passed":
            continue
        method_name = _method_from_intent(f.get("intent") or "")
        if not method_name:
            unknown += 1
            per_method.append({"feature": f.get("id"), "status": status, "method": None})
            continue
        passed = _match_method_passed(method_name, method_results)
        per_method.append({"feature": f.get("id"), "status": status, "method": method_name, "method_passed": passed})
        if passed is True:
            f1_count += 1
        elif passed is False:
            f3_count += 1
        else:
            unknown += 1

    if f1_count and not f3_count:
        record["label"] = "F1"
    elif f3_count and not f1_count:
        record["label"] = "F3"
    elif f1_count and f3_count:
        record["label"] = "F0_mixed"
    else:
        record["label"] = "unknown"

    record["detail"] = f"F1={f1_count} F3={f3_count} unknown_methods={unknown}"
    record["per_feature"] = per_method
    return record


def main():
    print(f"{'task':<14} {'model':<7} {'config':<18} {'label':<10} detail")
    print("-" * 110)

    tally = Counter()
    rows: list[dict] = []

    for model in ("sonnet", "haiku"):
        for cfg in ("tdd_loop", "tdd_loop_oracle"):
            base = RUNS / model / cfg
            if not base.exists():
                continue
            for d in sorted(base.iterdir(), key=lambda p: int(p.name.split("_")[-1]) if p.name.startswith("ClassEval_") else 1e9):
                if not (d / "result.json").exists():
                    continue
                r = classify_task(d)
                rows.append(r)
                if r.get("label") == "PASS":
                    continue
                tally[(model, cfg, r["label"])] += 1
                print(f"{r.get('task_id',''):<14} {r.get('model',''):<7} {r.get('config',''):<18} {r['label']:<10} {r.get('detail','')}")

    print()
    print("=== Distribution by (model, config, label) ===")
    for (model, cfg), _ in sorted({(k[0], k[1]): None for k in tally}.items()):
        print(f"\n[{model}/{cfg}] (failed tasks only)")
        subtotal = sum(v for k, v in tally.items() if k[0] == model and k[1] == cfg)
        for k in sorted([k for k in tally if k[0] == model and k[1] == cfg]):
            n = tally[k]
            print(f"  {k[2]:<10} {n:>2} ({n/subtotal:.0%})")
        print(f"  {'TOTAL':<10} {subtotal:>2}")

    out = RUNS / "_failure_classification.json"
    out.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nFull per-task labels written to {out}")


if __name__ == "__main__":
    main()
