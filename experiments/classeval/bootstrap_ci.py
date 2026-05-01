# -*- coding: utf-8 -*-
"""Paired bootstrap 95% CIs for the headline pass@1 contrasts.

We have one observation per (task, model, config). For paired contrasts
(e.g. tdd_loop vs baseline within the same model), tasks are matched by
task_id, so the bootstrap resamples task_ids with replacement and
recomputes the difference of means.
"""
from __future__ import annotations

import glob
import json
import random
from pathlib import Path

RUNS = Path("E:/AICoding/Paper/experiments/classeval/runs")
B = 10_000  # bootstrap iterations
SEED = 42


def collect_pass_dict(model: str, config: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for f in glob.glob(str(RUNS / model / config / "ClassEval_*" / "result.json")):
        try:
            r = json.loads(Path(f).read_text(encoding="utf-8"))
        except Exception:
            continue
        tid = r.get("task_id")
        ev = r.get("eval") or {}
        out[tid] = 1 if ev.get("class_passed") else 0
    return out


def paired_bootstrap(a: dict[str, int], b: dict[str, int], B: int = B, seed: int = SEED) -> tuple[float, float, float]:
    common = sorted(set(a) & set(b))
    if not common:
        return float("nan"), float("nan"), float("nan")
    pairs = [(a[t], b[t]) for t in common]
    n = len(pairs)
    diff_mean = sum(x - y for x, y in pairs) / n
    rng = random.Random(seed)
    diffs = []
    for _ in range(B):
        s = [pairs[rng.randrange(n)] for _ in range(n)]
        diffs.append(sum(x - y for x, y in s) / n)
    diffs.sort()
    lo = diffs[int(0.025 * B)]
    hi = diffs[int(0.975 * B)]
    return diff_mean, lo, hi


def main():
    print(f"Paired bootstrap, B={B}, seed={SEED}")
    print(f"Δ pass@1 = config_a − config_b (positive ⇒ a > b)\n")

    contrasts = [
        # (label, model_a, config_a, model_b, config_b)
        ("Sonnet · tdd_loop          − baseline",          "sonnet", "tdd_loop",         "sonnet", "baseline"),
        ("Sonnet · tdd_loop_oracle   − baseline_oracle",   "sonnet", "tdd_loop_oracle",  "sonnet", "baseline_oracle"),
        ("Sonnet · tdd_loop_oracle   − tdd_loop  (oracle rescue)", "sonnet", "tdd_loop_oracle",  "sonnet", "tdd_loop"),
        ("Sonnet · baseline_oracle   − baseline   (oracle on baseline)",   "sonnet", "baseline_oracle",  "sonnet", "baseline"),
        ("Haiku  · tdd_loop          − baseline",          "haiku",  "tdd_loop",         "haiku",  "baseline"),
        ("Haiku  · tdd_loop_oracle   − baseline_oracle",   "haiku",  "tdd_loop_oracle",  "haiku",  "baseline_oracle"),
        ("Haiku  · tdd_loop_oracle   − tdd_loop  (oracle rescue)", "haiku",  "tdd_loop_oracle",  "haiku",  "tdd_loop"),
        ("Haiku  · baseline_oracle   − baseline   (oracle on baseline)",   "haiku",  "baseline_oracle",  "haiku",  "baseline"),
        # cross-model: does Haiku+tdd_loop_oracle equal Sonnet+tdd_loop_oracle?
        ("Cross  · Haiku tdd_loop_oracle − Sonnet tdd_loop_oracle", "haiku", "tdd_loop_oracle", "sonnet", "tdd_loop_oracle"),
    ]

    print(f"{'contrast':<70} {'n':>3} {'Δ':>8} {'95% CI':<22} {'sig.'}")
    print("-" * 110)
    for (label, ma, ca, mb, cb) in contrasts:
        a = collect_pass_dict(ma, ca)
        b = collect_pass_dict(mb, cb)
        d, lo, hi = paired_bootstrap(a, b)
        n = len(set(a) & set(b))
        sig = "**" if (lo > 0 or hi < 0) else "  "
        print(f"{label:<70} {n:>3} {d:>+7.1%} [{lo:>+5.1%}, {hi:>+5.1%}]  {sig}")
    print("\n** = 95% CI excludes 0 (significant at α=0.05)")


if __name__ == "__main__":
    main()
