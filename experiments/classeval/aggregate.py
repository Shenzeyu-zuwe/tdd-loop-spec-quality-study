# -*- coding: utf-8 -*-
"""Aggregate per-task result.json files into a single summary.

Walks runs/<model>/<config>/<task_id>/result.json. Source of truth is the
per-task file (the runner overwrites it on re-run), so this is robust to
recovery runs that patched only a subset of tasks.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

RUNS = Path(__file__).resolve().parent / "runs"


def collect(model: str, config: str) -> list[dict]:
    base = RUNS / model / config
    if not base.exists():
        return []
    rows = []
    for task_dir in sorted(base.iterdir(), key=lambda p: int(p.name.split("_")[-1]) if p.name.startswith("ClassEval_") else 1e9):
        rj = task_dir / "result.json"
        if not rj.exists():
            continue
        try:
            rows.append(json.loads(rj.read_text(encoding="utf-8")))
        except Exception as e:
            print(f"  WARN: failed to read {rj}: {e}", file=sys.stderr)
    return rows


def summarize(rows: list[dict]) -> dict:
    n = len(rows)
    valid = [r for r in rows if r.get("gen_status") not in ("error",) or (r.get("eval") or {}).get("ok")]
    # class_passed counts only over rows where eval ran
    evaluated = [r for r in rows if (r.get("eval") or {}).get("ok") is not None and (r.get("eval") or {}).get("class_passed") is not None]
    passed = sum(1 for r in rows if (r.get("eval") or {}).get("class_passed"))
    method_pass = sum((r.get("eval") or {}).get("method_pass_count") or 0 for r in rows)
    method_total = sum((r.get("eval") or {}).get("method_total") or 0 for r in rows)
    quota_errors = sum(1 for r in rows if r.get("gen_status") == "error" and r.get("gen_cost_usd", 0) == 0 and "429" in (r.get("error") or ""))
    cost = sum(r.get("gen_cost_usd", 0) or 0 for r in rows)
    duration = sum(r.get("gen_duration_s", 0) or 0 for r in rows)
    return {
        "n_tasks": n,
        "class_passed": passed,
        "class_pass_rate": round(100 * passed / n, 1) if n else 0.0,
        "method_passed": method_pass,
        "method_total": method_total,
        "method_pass_rate": round(100 * method_pass / method_total, 1) if method_total else 0.0,
        "quota_429_errors": quota_errors,
        "total_cost_usd": round(cost, 4),
        "total_duration_s": round(duration, 1),
        "avg_cost_per_task": round(cost / n, 4) if n else 0.0,
    }


def main():
    models = sys.argv[1:] or ["sonnet", "haiku", "opus"]
    print(f"{'model':<8} {'config':<10} {'n':>3} {'pass':>6} {'rate':>6} {'methods':>10} {'mrate':>6} {'cost':>10} {'avg':>8} {'q429':>5}")
    print("-" * 90)
    for model in models:
        for cfg in ("baseline", "baseline_oracle", "tdd_loop", "tdd_loop_oracle"):
            rows = collect(model, cfg)
            if not rows:
                continue
            s = summarize(rows)
            print(f"{model:<8} {cfg:<10} {s['n_tasks']:>3} "
                  f"{s['class_passed']:>6} {s['class_pass_rate']:>5}% "
                  f"{s['method_passed']:>4}/{s['method_total']:<5} {s['method_pass_rate']:>5}% "
                  f"${s['total_cost_usd']:>8.4f} ${s['avg_cost_per_task']:>6.4f} {s['quota_429_errors']:>5}")
    print()


if __name__ == "__main__":
    main()
