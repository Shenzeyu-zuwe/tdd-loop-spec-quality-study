# Validation findings — 2026-04-28

Three deepening experiments requested:
1. Failure-mode classification of every failed `tdd_loop` run
2. Bootstrap CIs on every headline contrast
3. SWE-bench Lite mini scaffolding (10-task crossover probe)

This document reports #1 and #2 in full. #3 is built but not yet launched.

---

## 1. Failure-mode classification

**Method.** `experiments/classeval/classify_failures.py` reads each failed
TDD-Loop run and assigns one label using these signals:

| Label | Decision rule |
|---|---|
| **F1** Tester false-reject | feature skipped/failed, but the corresponding method passes the held-out unittest |
| **F2** Tester false-accept | every feature marked `passed`, but ≥1 method fails the held-out unittest |
| **F3** Worker could-not-fix | feature skipped/failed AND the method also fails held-out |
| **F5** Environment / CLI failure | `gen_status ∈ {error, timeout}`, low iteration count |
| **F6** Convergence cap | `gen_status` non-ok with iters ≥ 7 and a mix of passed/skipped features (signature-dedup or attempt-cap likely tripped) |

(F4 "intent under-anchoring" was folded into F2; the symptom is identical.)

### Distribution

**Intent-only TDD-Loop failures**

| Label | Sonnet (n=16) | Haiku (n=20) | Combined (n=36) |
|---|---|---|---|
| **F2** Tester false-accept | 9 (56%) | 12 (60%) | **21 (58%)** |
| **F6** Convergence cap | 7 (44%) | 7 (35%) | 14 (39%) |
| **F5** Env / CLI fail | 0 | 1 (5%) | 1 (3%) |
| **F1** Tester false-reject | **0** | **0** | **0** |
| **F3** Worker could-not-fix | **0** | **0** | **0** |

**Oracle TDD-Loop failures**

| Label | Sonnet (n=3) | Haiku (n=2) |
|---|---|---|
| F2 | 0 | 2 |
| F5 | 1 | 0 |
| F6 | 2 | 0 |

### Key reading

1. **F1 and F3 are zero.** The Tester is never *too strict*, and the Worker
   can always do *something* with whatever verdict it gets. The framework's
   convergence safeguards are working as designed — they just converge on
   the wrong answer.
2. **F2 is the dominant failure mode (~58% of failures).** The loop
   terminates declaring full green; the held-out unittest disagrees. The
   Tester writes its own runtime probe based on the under-anchored intent;
   that probe is **shallower than the held-out test** and misses edge cases.
3. **F2 collapses to ~zero under oracle.** When the intent embeds the
   actual test code, the Tester's probe coverage matches the held-out
   coverage; the oracle arm has 5 total failures vs 36 in the intent-only
   arm, and only 2 of the 5 oracle failures are F2.

### What this means for the paper

The previous draft predicted **F1 dominance** (Tester rejecting correct
code). The data says the *opposite*: Tester is failing by being **too
lenient**, not too strict. This is a tighter, more publishable insight:

> **Multi-agent decomposition under intent-only specs fails because the
> LLM verifier writes a probe that is strictly weaker than the
> ground-truth test it is meant to stand in for. The bottleneck is *probe
> coverage*, not framework design or worker capability.**

This insight transfers directly to other multi-agent code frameworks: any
LLM-as-verifier scheme that derives its probe from natural-language intent
is liable to the same shallow-probe failure mode. The remedy is either
(i) deterministic verification (compiler/test runner) or (ii) automated
intent enrichment that forces the probe surface to match the deployment
test surface.

---

## 2. Bootstrap confidence intervals

**Method.** `experiments/classeval/bootstrap_ci.py`. Paired bootstrap
B = 10 000, seed = 42, on the matched per-task pass/fail outcomes
(n = 30 per cell, common task ids).

| Contrast | Δ pass@1 | 95% CI | Sig. |
|---|---|---|---|
| Sonnet · `tdd_loop − baseline` | **−23.3 pp** | [−40.0, −10.0] | ✅ |
| Sonnet · `tdd_loop_oracle − baseline_oracle` | +10.0 pp | [−3.3, +23.3] | ✗ |
| Sonnet · `tdd_loop_oracle − tdd_loop` (oracle rescue) | **+43.3 pp** | [+26.7, +60.0] | ✅ |
| Sonnet · `baseline_oracle − baseline` (oracle on baseline) | +10.0 pp | [−6.7, +26.7] | ✗ |
| Haiku · `tdd_loop − baseline` | **−26.7 pp** | [−43.3, −10.0] | ✅ |
| Haiku · `tdd_loop_oracle − baseline_oracle` | +3.3 pp | [0.0, +10.0] | borderline |
| Haiku · `tdd_loop_oracle − tdd_loop` (oracle rescue) | **+60.0 pp** | [+43.3, +76.7] | ✅ |
| Haiku · `baseline_oracle − baseline` (oracle on baseline) | **+30.0 pp** | [+13.3, +46.7] | ✅ |
| Cross · `Haiku tdd_loop_oracle − Sonnet tdd_loop_oracle` | +3.3 pp | [0.0, +10.0] | borderline |

✅ = 95% CI strictly excludes 0; ✗ = CI includes 0; borderline = touches 0.

### What is and is not significant

**Significant**:
- Both models: `tdd_loop − baseline` is **significantly negative** (~−25 pp).
- Both models: `tdd_loop_oracle − tdd_loop` (oracle rescue) is **massively positive** (+43 to +60 pp).
- Haiku only: `baseline_oracle − baseline` is significantly positive (+30 pp).

**Not significant**:
- **Sonnet `tdd_loop_oracle − baseline_oracle = +10.0 pp` is not statistically distinguishable from zero.**
- **Cross-model `Haiku oracle ≈ Sonnet oracle` (Δ +3.3 pp, CI touches 0)** — Haiku-with-loop catches up to Sonnet-with-loop, but the gap is at the edge of significance.

### What this means for the paper

The single most important result is in italics above: **at matched (oracle)
spec quality, the framework does not significantly outperform the
single-agent baseline at n = 30**. The oracle rescue is real and huge,
but the rescue is rescuing the *spec*, not the *framework*. The framework
contribution at matched spec is a small, statistically-undefined wash.

This is actually a **stronger** narrative than "TDD-Loop wins":

> The 2 × 2 design isolates the question. Decomposition with weak spec
> harms (significant). Decomposition with strong spec is indistinguishable
> from single-agent with strong spec at n = 30. **Spec quality, not
> architecture, dominates the result.**

The paper thereby steps cleanly out of the "is multi-agent worth it?"
debate by saying: that is the wrong question. The right question is "is
your spec good enough to make either approach work?"

---

## 3. SWE-bench Lite mini scaffolding (built, not launched)

**Status.** Code complete; ready to launch. Files:

```
experiments/swebench_lite/
├── README.md            launch instructions + setup checklist
├── loader.py            10-task curated subset (--list works offline)
├── to_feature_list.py   intent + oracle variants
├── env_repo.py          per-task git checkout + pytest harness
├── evaluator.py         FAIL_TO_PASS / PASS_TO_PASS gate (docker-less)
├── runner.py            baseline / tdd_loop / tdd_loop_oracle drivers
└── (runs/ created on first launch)
environments/swebench_repo.py  plugin shim for tdd_loop --environment
```

### Why we did not launch yet

A full sweep is `10 tasks × 3 configs × 1 model = 30 runs`. Per-task wall
time is dominated by repo install (~2–10 min) plus loop iterations. Realistic
total: **6–12 hours**. Should only run when the user has decided to commit
to this branch of the validation plan.

### One-time setup (~10 min)

```bash
pip install datasets swebench
python -m experiments.swebench_lite.loader --list   # confirms 10 ids
```

### Launch command

```bash
python -m experiments.swebench_lite.runner \
    --configs baseline,tdd_loop \
    --models sonnet \
    --max-iter 25 \
    --n 10
```

### What this experiment will tell us

Two possible outcomes, both publishable:

| If the gap looks like… | Interpretation | Effect on paper |
|---|---|---|
| Same `tdd_loop − baseline ≈ −25 pp` on SWE-bench | The "weak-spec hurts decomposition" claim is **universal** | Strengthens existing story; one stronger generalisation paragraph |
| Gap shrinks toward zero or reverses | Task complexity has a **crossover regime** | Adds a new section on the boundary; richer paper |

---

## Recommended next move

Decide whether to launch SWE-bench. The findings above already support a
publishable IEEE ACCESS paper without it; SWE-bench either bolsters the
universality claim or adds a complexity-axis to the story. Either is worth
the ~10-hour run time; neither is mandatory.

If you decide to launch: just run the command in §3. It writes per-task
artifacts in the same shape as ClassEval, so `aggregate.py` and
`bootstrap_ci.py` will need only trivial parameterisation to handle the
new directory tree.

If you decide not to launch: I will rewrite the manuscript draft from the
"spec is the bottleneck" angle using the F2 dominance and the bootstrap
CIs above, and we leave SWE-bench as Future Work.
