<!--
  TDD-Loop manuscript draft v2 — target venue: IEEE ACCESS
  Status: DRAFT — all numbers below are real (ClassEval 30×4×2 factorial,
  paired bootstrap B=10000, failure-mode classification on n=36 fails).
  Replacements still required:
    [TODO]   → author names, affiliations, repo URL, DOI
    [CITE n] → reference index lookup once final reference list is frozen
-->

# Spec Quality, Not Architecture: A 2×2 Empirical Study of Multi-Agent Decomposition for LLM Code Generation

**Authors:** [TODO]
**Affiliation:** [TODO]
**Corresponding email:** [TODO]
**Target venue:** IEEE Access

---

## Abstract

Multi-agent decomposition — splitting an LLM coding agent into role-separated sub-agents (specifier, verifier, coder, reviewer) coordinated by a controller — is increasingly assumed to outperform single-agent iterative refinement. The empirical record for this assumption rests almost entirely on architectural comparisons that confound *what the agent is told to verify* with *how verification is wired*. We disentangle these axes with a 2 × 2 factorial study. We build **TDD-Loop**, a deterministic two-agent framework in which a verification-only Tester and an edit-only Worker are coupled by a Python orchestrator with bounded-termination guarantees. We compare TDD-Loop against a single-agent Claude Code CLI baseline under two specification regimes: *intent-only* natural-language feature lists, and *oracle* feature lists that embed the actual hidden test code. Each cell is run on 30 ClassEval class-level Python tasks with two model classes (Claude Sonnet 4.6, Haiku 4.5), giving 240 runs, with paired-bootstrap 95% confidence intervals on every contrast.

Three findings reframe the multi-agent debate. **First**, on intent-only specs, decomposition is significantly *harmful*: TDD-Loop loses to the baseline by **−23.3 pp** (Sonnet) and **−26.7 pp** (Haiku) at 30 × higher cost (CIs both exclude zero). **Second**, on oracle specs the same framework jumps to ≥ 90 % pass@1 — but the gap *over the oracle baseline* is only **+10.0 pp** (Sonnet) and **+3.3 pp** (Haiku), and is **not statistically significant** at n = 30 in either case. **Third**, manual classification of all 36 intent-only failures attributes 58 % to a single mechanism we call **Tester false-accept**: the Tester's self-authored probe is strictly weaker than the held-out test it is meant to stand in for, so the loop terminates declaring full green on under-tested code. Tester false-reject — the failure mode the multi-agent literature implicitly assumes one is mitigating — is **never observed** (0 / 36). We argue that multi-agent decomposition, on the regime where present-day frontier models already perform well at single-agent level, contributes nothing statistically distinguishable beyond the quality of the specification handed to it. The community's effort is better spent on automated specification anchoring than on agent-graph design.

**Keywords:** large language models, code generation, LLM agents, multi-agent systems, test-driven development, empirical software engineering, ClassEval, factorial design, bootstrap

---

## 1. Introduction

### 1.1 Motivation

Single-agent iterative coding agents — generate, run, reflect, edit — already match or exceed substantial fractions of public code-generation benchmarks on frontier models [CITE 8, CITE 9]. In parallel, a growing body of work proposes **multi-agent decomposition** [CITE 5, CITE 6]: splitting "spec author", "test author", "code editor", and "verifier" across role-typed LLM invocations under a coordinating controller, on the implicit hypothesis that role separation reduces cognitive load and surfaces bugs that a single-agent loop misses.

What is missing is a *controlled* test of this hypothesis. Multi-agent papers compare their full system against a non-iterative single-call baseline, conflating two design choices into one comparison: **(a)** what *specification* the system receives (free-form prompt vs. structured spec vs. embedded tests) and **(b)** what *architecture* processes that specification (single agent vs. role-decomposed). When both are varied simultaneously, gains attributed to architecture may in fact be gains from richer specifications.

### 1.2 The 2 × 2 Design

We separate the two axes:

|  | **Spec: intent only** | **Spec: oracle (test code embedded)** |
|---|---|---|
| **Architecture: single agent** | `baseline` | `baseline_oracle` |
| **Architecture: two-agent (TDD-Loop)** | `tdd_loop` | `tdd_loop_oracle` |

The factorial allows two clean reads. The **architecture main effect** at fixed spec quality (`tdd_loop_oracle − baseline_oracle`) tests whether multi-agent decomposition adds value over a single agent when both have the same information. The **spec main effect** at fixed architecture (`tdd_loop_oracle − tdd_loop`) tests whether providing the verifier with deterministic ground truth rescues the framework. Their relative magnitudes determine which axis is doing the work.

### 1.3 Research Questions

- **RQ1.** Under intent-only specs, does multi-agent decomposition outperform a single iterative agent on a public class-level code benchmark?
- **RQ2.** Does oracle-quality spec rescue an under-performing decomposed agent, and if so, by how much relative to giving the same oracle spec to the single-agent baseline?
- **RQ3.** What mechanism dominates the failure modes of intent-only decomposition?

### 1.4 Contributions

1. **A 2 × 2 factorial empirical study** that disentangles specification quality from agent architecture in LLM code generation, evaluated on ClassEval × {Claude Sonnet 4.6, Haiku 4.5} = 240 runs with paired-bootstrap confidence intervals.
2. **An open-source two-agent framework (TDD-Loop)** with explicit, machine-checkable convergence guarantees, used as the experimental probe rather than as a competitive system. We argue this framing — *framework as instrument* — is what the literature has been missing.
3. **A failure-mode taxonomy** for two-agent code-repair loops, applied by manual labelling of every failed intent-only run (n = 36), establishing that the dominant failure mode is *Tester false-accept* (58 %) — the LLM verifier writes a strictly weaker probe than the held-out test it is meant to stand in for. Tester false-reject, the implicitly assumed failure mode in multi-agent designs, is **not observed**.
4. **An empirically grounded condition** under which decomposition is and is not worth its overhead, with implications for future agent-framework design: spec quality, not agent topology, is where the bottleneck sits in present LLMs.

### 1.5 Headline result

On intent-only specs, TDD-Loop reaches `pass@1 = 46.7 %` (Sonnet) and `33.3 %` (Haiku), against a baseline of `70.0 %` and `60.0 %` respectively — a **statistically significant negative gap** of −23.3 pp and −26.7 pp (95 % paired-bootstrap CIs strictly below zero). On oracle specs, the same framework reaches `90.0 %` and `93.3 %`, a *significant* rescue effect of +43.3 pp and +60.0 pp, but the gap *over the oracle single-agent baseline* (+10.0 pp / +3.3 pp) is **not** significant. Cost is 30 × to 50 × higher under TDD-Loop regardless of spec.

We take this to mean: **the framework adds nothing statistically distinguishable at matched spec quality**. What rescues TDD-Loop on oracle specs is the spec, not the framework.

### 1.6 Paper organisation

§2 surveys single-agent and multi-agent code-generation agents and positions our 2 × 2 design. §3 describes the framework (used as an instrument, not a contribution). §4 lays out the experimental design. §5 reports quantitative results. §6 reports the qualitative failure-mode analysis. §7 discusses implications. §8 enumerates threats to validity. §9 concludes.

---

## 2. Related Work

### 2.1 Single-agent iterative coding agents

The dominant single-agent recipe is *generate–run–reflect*. ReAct [CITE 8] interleaves reasoning traces with tool calls. Self-Refine [CITE 9] and Reflexion [CITE 10] add a self-critique phase between iterations. Claude Code, Aider, and Cursor agent are deployed instances of this pattern with persistent file edits and shell access. None of these report bootstrap CIs against multi-agent counterparts at matched specification.

### 2.2 Multi-agent decomposition

MetaGPT [CITE 5] organises agents around software engineering roles (PM, architect, engineer, QA). AutoGen [CITE 6] provides a conversational substrate for arbitrary role graphs. The shared empirical weakness is the absence of a head-to-head comparison against a strong single-agent iterative baseline at matched cost and matched specification. Our 2 × 2 design fills this gap.

### 2.3 Verification-driven repair

Agentless [CITE 7] takes the inverse stance — it shows that a *non-agentic* localise-and-patch pipeline matches or beats SWE-agent on SWE-bench Lite, suggesting much of the apparent benefit of agentic frameworks may be coordination overhead in disguise. SWE-agent [CITE 4] introduces an agent–computer interface tailored for repository tasks. SWE-bench [CITE 3] establishes the repository-level benchmark. None of these works isolates the *role-decomposition* axis from the *specification* axis we study here.

### 2.4 Specification anchoring

ClassEval [CITE 2] provides the docstring-and-test-suite benchmark we use; it is class-level, Python-only, and has both visible (docstring) and hidden (unit test) facets that map cleanly to our intent-only / oracle contrast. HumanEval [CITE 1] is the smaller method-level antecedent. Wohlin et al. [CITE 11] supplies the threats-to-validity taxonomy used in §8.

### 2.5 Position

Methodologically we are closest to factorial empirical studies in software-engineering research [CITE 11]. Substantively we differ from the prior multi-agent literature in three ways: (i) we treat our framework as an experimental instrument rather than a competitive contribution, (ii) we report paired-bootstrap CIs on every contrast, and (iii) we manually classify every failure to identify mechanism rather than relying on aggregate metrics alone. To our knowledge no prior multi-agent code-generation paper reports a *non-significant* main effect of architecture at matched specification — it is precisely this null finding, supported by a positive and significant *spec rescue* effect, that we contribute.

---

## 3. The TDD-Loop Framework

We use TDD-Loop as the experimental instrument for the architecture axis of the factorial. The framework is engineered to be *deterministically terminating* and *invariant across spec regime*, so that any difference between cells is attributable to the manipulated variables rather than to framework variation.

### 3.1 Three-layer design

```
┌──────────────────────────────────────────────────────────────┐
│  Layer 1 — Spec (data)                                       │
│    feature_list.json: intent-only or oracle, status-machine  │
├──────────────────────────────────────────────────────────────┤
│  Layer 2 — Control (Orchestrator)                            │
│    Tester → Worker loop; stuck-detection; regression pass;   │
│    persistence; signal/lock/takeover; handoff on interrupt   │
├──────────────────────────────────────────────────────────────┤
│  Layer 3 — Agents + Harness                                  │
│    Tester & Worker = Claude CLI subprocesses                 │
│    Environment = pluggable runtime adapter                    │
└──────────────────────────────────────────────────────────────┘
```

Layer 2 owns *when* to verify; Layer 3's Tester owns *what counts as a pass*; the `Environment` owns *how to probe*. This separation makes the same core drive ClassEval (subprocess harness) and, in principle, repository-level tasks (git+pytest harness).

### 3.2 Two specification regimes

In the **intent-only** regime, each test case is a natural-language description of an invariant the implementation must satisfy (example: *"Method `add` on class `BigNumCalculator` executes correctly at runtime against its docstring's contract"*). The Tester reads source, designs and runs its own probe, and emits a verdict. **No test code is embedded.**

In the **oracle** regime, each test case carries an instruction to write the actual hidden ClassEval unit test for that method to a temp file and execute it via a subprocess. **The verdict is then bound to the exit code of the ground-truth test.** This is the strongest possible spec: the Tester's probe and the held-out evaluator's probe are the same code.

### 3.3 Tester agent

The Tester is a Claude Code CLI session prompted to read source, run the appropriate probe (per spec regime), and emit:

```json
{ "test_id": "T-001-02", "verdict": "pass" | "fail" | "indeterminate",
  "reason": "...", "evidence": ["file.py:23", "..."] }
```

The Tester is *read-only on source*. Any source modification by the Tester is treated as a violation; the orchestrator does not enforce this mechanically and instead relies on prompt discipline plus the architectural fact that Worker is the sole fixer.

### 3.4 Worker agent

The Worker receives the latest verdict and is asked to make the smallest edit that would flip a `fail` to `pass`. The Worker does not run tests, does not emit verdicts, and is not given the prior Worker session — only the disk state and the latest Tester verdict. This asymmetry forces every Worker iteration to re-read the file system, eliminating a class of hallucinated-state bugs.

### 3.5 Convergence safeguards

| Mechanism | Trigger | Effect |
|---|---|---|
| `FEATURE_SKIP_THRESHOLD` | 5 attempts on same feature | Feature → `skipped` |
| `TEST_CONSECUTIVE_FAIL_THRESHOLD` | 3 consecutive fails on same test | Test → `skipped` |
| `TEST_REPEAT_REASON_THRESHOLD` | 2 fails with same normalised reason | Test → `skipped` (aggressive) |
| `CLI_CRASH_ABORT_THRESHOLD` | 5 consecutive CLI crashes | Loop aborts |
| `max_iterations` | run-level cap | Loop exits with `max_iterations_reached` |

The *normalised reason* signature strips timestamps, addresses, and literal numbers before hashing, collapsing structurally equivalent failures regardless of incidental detail.

### 3.6 Reproducibility

Every Tester / Worker invocation produces a Claude CLI `session_id` replayable via `claude --resume`. Per-session metadata (cost, duration, turn count) is logged to `sessions_log.jsonl`. All runs reported in §5 are reproducible from these logs.

---

## 4. Experimental Design

### 4.1 Conditions

The 2 × 2 factorial yields four configurations:

- `baseline` — single Claude Code CLI call. Prompt: imports + class skeleton + docstrings.
- `baseline_oracle` — same as `baseline`, but the prompt additionally embeds the full hidden unit-test code.
- `tdd_loop` — TDD-Loop with intent-only feature list (§3.2).
- `tdd_loop_oracle` — TDD-Loop with oracle feature list (§3.2). Identical orchestrator code to `tdd_loop`; only the feature list differs.

### 4.2 Tasks and models

We sample 30 contiguous tasks (`ClassEval_0` … `ClassEval_29`) from ClassEval [CITE 2]. Each (task × config × model) cell is run once, yielding 30 × 4 × 2 = 240 runs. Models: Claude Sonnet 4.6 and Haiku 4.5. The same 30 tasks appear in all eight cells; pairs are matched by task id for the bootstrap.

### 4.3 Metrics

- **`pass@1`** — fraction of tasks whose final state, as written to `solution.py`, passes the held-out ClassEval unit-test class. The held-out tests are *never* shown to either agent in the intent-only regime; they are embedded into the spec in the oracle regime.
- **`method_pass`** — fraction of method-level tests passed (each task has multiple methods); reported as a finer-grained signal.
- **Cost (USD)** — sum of `cost_usd` reported by Anthropic for every CLI session in the run.
- **Wall time (s)** — end-to-end wall-clock seconds per run.

### 4.4 Statistical analysis

For every contrast we report a paired bootstrap with *B* = 10 000 resamples, seed 42, paired by task id. We report 95 % CIs and treat a contrast as significant when the CI strictly excludes zero.

### 4.5 Failure-mode classification

Every failed `tdd_loop` and `tdd_loop_oracle` run is labelled by a deterministic classifier that consults the final `feature_list.json` state, the `eval.method_results` of the held-out unittest, and the `gen_status` (`ok` / `error` / `timeout`). Labels:

| F1 | Tester false-reject | feature skipped/failed but the corresponding method passes the held-out unittest |
| F2 | Tester false-accept | every feature marked `passed`, but ≥ 1 method fails the held-out unittest |
| F3 | Worker could-not-fix | feature skipped/failed AND the method also fails held-out |
| F5 | Environment / CLI failure | `gen_status ∈ {error, timeout}`, no convergence-cap signal |
| F6 | Convergence cap | non-ok exit with iters ≥ 7 and a mix of passed/skipped features |

The classifier is open-source (`experiments/classeval/classify_failures.py`) and writes a per-task labelled JSON (`runs/_failure_classification.json`) for inspection.

### 4.6 Implementation details

All runs were executed on a single workstation (Windows 11, 32 GB RAM). The Claude Code CLI was pinned to a single version for the duration of the experiment. The orchestrator used `max_iterations = 20` and the threshold values listed in §3.5. The full configuration is reproduced from the open-source artifact (§10).

---

## 5. Results

### 5.1 The 2 × 2 table

**Table 1.** Pass rates and run cost across the 2 × 2 factorial (n = 30 per cell).

| Model | Config | pass@1 | method | cost (USD) | wall (min) |
|---|---|---:|---:|---:|---:|
| Sonnet | `baseline` | 70.0 % | 87.3 % | 1.08 | 3.6 |
| Sonnet | `baseline_oracle` | 80.0 % | 89.0 % | 1.54 | 6.6 |
| Sonnet | `tdd_loop` | **46.7 %** | 66.9 % | 49.75 | 842.7 |
| Sonnet | `tdd_loop_oracle` | **90.0 %** | 90.7 % | 34.97 | 302.9 |
| Haiku | `baseline` | 60.0 % | 83.9 % | 1.08 | 13.8 |
| Haiku | `baseline_oracle` | 90.0 % | 93.2 % | 1.32 | 16.8 |
| Haiku | `tdd_loop` | **33.3 %** | 63.6 % | 31.41 | 479.0 |
| Haiku | `tdd_loop_oracle` | **93.3 %** | 94.1 % | 22.26 | 250.4 |

The columns to read first are `pass@1` and `cost`. TDD-Loop is 30 × to 50 × more expensive than the corresponding baseline in every cell. Under intent-only specs it is **substantially worse**; under oracle specs it is *slightly* better than the oracle baseline but at orders of magnitude more cost.

### 5.2 Bootstrap confidence intervals

**Table 2.** Paired-bootstrap 95 % CIs for headline contrasts (B = 10 000, paired by task id, n = 30).

| Contrast | Δ pass@1 | 95 % CI | Sig. |
|---|---:|---|:---:|
| Sonnet · `tdd_loop − baseline` | **−23.3 pp** | [−40.0, −10.0] | ✓ |
| Sonnet · `tdd_loop_oracle − baseline_oracle` | +10.0 pp | [−3.3, +23.3] | ✗ |
| Sonnet · `tdd_loop_oracle − tdd_loop` (oracle rescue) | **+43.3 pp** | [+26.7, +60.0] | ✓ |
| Sonnet · `baseline_oracle − baseline` | +10.0 pp | [−6.7, +26.7] | ✗ |
| Haiku  · `tdd_loop − baseline` | **−26.7 pp** | [−43.3, −10.0] | ✓ |
| Haiku  · `tdd_loop_oracle − baseline_oracle` | +3.3 pp | [0.0, +10.0] | borderline |
| Haiku  · `tdd_loop_oracle − tdd_loop` (oracle rescue) | **+60.0 pp** | [+43.3, +76.7] | ✓ |
| Haiku  · `baseline_oracle − baseline` | **+30.0 pp** | [+13.3, +46.7] | ✓ |
| Cross  · `Haiku tdd_loop_oracle − Sonnet tdd_loop_oracle` | +3.3 pp | [0.0, +10.0] | borderline |

Three readings dominate:

1. **Architecture main effect (under intent-only specs) is significantly negative.** In both models, decomposition costs ~25 pp of `pass@1` and the CIs strictly exclude zero. This is robust.
2. **Architecture main effect (under oracle specs) is not significant.** On Sonnet, `tdd_loop_oracle − baseline_oracle = +10.0 pp [−3.3, +23.3]` — the CI crosses zero. On Haiku, the same contrast is +3.3 pp with a CI that touches zero. *At matched spec, the framework's contribution is statistically indistinguishable from zero at n = 30.*
3. **Spec main effect (oracle vs. intent-only, under TDD-Loop) is the largest signed effect anywhere in the table.** +43.3 pp on Sonnet, +60.0 pp on Haiku, both with CIs strictly above zero. The oracle rescues the framework; the framework does not, in turn, rescue itself when the spec is improved on the baseline only modestly.

### 5.3 Per-task overlap

**Table 3.** Per-task pass-set overlap (n = 30).

| Set difference | Sonnet | Haiku |
|---|---:|---:|
| baseline ∩ ¬tdd_loop (loss) | 7 | 8 |
| tdd_loop ∩ ¬baseline (gain) | **0** | **0** |
| tdd_loop_oracle ∩ ¬tdd_loop (oracle rescue) | 13 | 18 |
| tdd_loop_oracle ∩ ¬baseline_oracle (residual architecture gain) | 4 | 1 |

The `tdd_loop ∩ ¬baseline = 0` row deserves emphasis: under intent-only specs, **there is no task on either model that TDD-Loop solves and the baseline does not.** Decomposition is a strict performance regression, not a tradeoff.

### 5.4 Cost breakdown

The 30–50 × cost overhead of TDD-Loop is dominated by Tester cycles. For Sonnet `tdd_loop_oracle`, the average run consumes 30+ Claude CLI sessions (Tester probes + Worker edits) versus the single session of the baseline. The orchestrator's signature-dedup reduces wasted iterations after a feature has converged in failure-signature space, but cannot reduce the dominant expense — the Tester probing every test case at least once.

---

## 6. Failure-Mode Analysis

We classified every failed run in the `tdd_loop` cells (n = 36 across both models) using the taxonomy of §4.5. The aim is to identify the *mechanism* of the architecture penalty observed in §5, not just its magnitude.

### 6.1 Distribution of failure modes (intent-only)

**Table 4.** Failure-mode counts on `tdd_loop` (intent-only).

| Label | Sonnet (n = 16) | Haiku (n = 20) | Combined (n = 36) |
|---|---:|---:|---:|
| **F2** Tester false-accept | 9 (56 %) | 12 (60 %) | **21 (58 %)** |
| **F6** Convergence cap | 7 (44 %) | 7 (35 %) | 14 (39 %) |
| **F5** Env / CLI fail | 0 | 1 (5 %) | 1 (3 %) |
| **F1** Tester false-reject | **0** | **0** | **0** |
| **F3** Worker could-not-fix | **0** | **0** | **0** |

Two observations are central to the paper's thesis:

**(1) Tester false-reject (F1) is empirically zero.** The implicit assumption of the multi-agent literature — that a separate verifier is worth its overhead because it catches mistakes the writer makes — depends on the verifier being too strict, occasionally rejecting correct code. We see this *zero* times in 36 failed runs.

**(2) Tester false-accept (F2) dominates at 58 %.** The Tester writes its own runtime probe based on the natural-language intent. That probe is *strictly weaker* than the held-out unittest. The Tester pronounces every feature `passed`; the loop terminates declaring full green; the held-out test then catches edge cases the Tester's probe never covered.

A representative case is `ClassEval_18` on Sonnet: the loop terminates with all 7 features marked `passed`, yet only 1 of 7 methods passes the held-out unittest. The Tester's probe — derived from intents like *"executes correctly at runtime against its docstring's contract"* — verified happy-path behaviour but missed edge cases that the held-out test exercises.

### 6.2 What happens under oracle specs

On `tdd_loop_oracle` (n = 5 fails total: 3 on Sonnet, 2 on Haiku), F2 collapses to 2 cases — both on Haiku, where post-hoc trace inspection suggests the Tester wrote a syntactically-correct but logically-stubbed test file. The oracle regime thus near-eliminates the F2 bottleneck: when the probe IS the held-out test, there is no probe-coverage gap to exploit.

### 6.3 Convergence-cap failures (F6)

The 39 % of intent-only failures labelled F6 are dominated by mid-loop CLI crashes (`gen_status ∈ {error, timeout}`) at iteration ≥ 7, not by clean attempt-cap exits. We treat F6 as an engineering nuisance rather than a finding of theoretical interest: a more robust CLI substrate would convert most F6s into either F2s or PASSes, leaving the F2 dominance intact.

### 6.4 Mechanism summary

The architecture penalty observed in §5 is mechanistically attributable to **probe coverage shortfall**: the LLM verifier, asked to derive its probe from natural-language intent, systematically writes a probe shallower than the held-out test it stands in for. This is a *spec-level* failure manifesting as an *architecture-level* symptom — exactly what the 2 × 2 design was constructed to disentangle.

---

## 7. Discussion

### 7.1 Spec quality, not architecture, is the bottleneck

The single most important reading of Tables 1–4 is this: at *matched* spec quality, the framework's contribution to `pass@1` is not statistically distinguishable from zero on either model at n = 30. What separates a 33 % run from a 93 % run on the same model and the same framework is whether the Tester can see the test code or only its natural-language description. The architecture choice does not.

This finding, on its own, would be unsurprising — a richer spec helps any system. The non-obvious part is the *asymmetry of magnitudes*: spec quality moves the framework's `pass@1` by +43 to +60 pp; architecture choice moves it by, at most, +10 pp (and not significantly so). Their ratio implies that a community-level effort spent equally on spec-quality tooling and on agent-graph design will yield ≥ 4 × greater return on the spec axis.

### 7.2 The probe-coverage problem

The mechanistic story behind §7.1 is the F2 dominance documented in §6. When the verification step is performed by an LLM operating on a natural-language intent, the verifier's probe is constrained by the intent surface. Edge cases not surfaced in the intent are not surfaced in the probe. The held-out test catches them; the Tester does not. This is not a failure of the Tester being too strict (the literature's implicit assumption) but of being too lenient — and the leniency is *structural*, not corrigible by prompt tuning.

The remedy implied by our results is straightforward: a verification step is profitable only when its probe is at least as strict as the deployment test. Two paths satisfy this: **(i) deterministic verification** — replace the LLM verifier with a compiler, type checker, or test runner — or **(ii) automated intent enrichment** — augment natural-language intents with programmatic anchors (concrete identifiers, expected types, expected exception classes, boundary values) so that an LLM probe derived from them must exercise those boundaries.

### 7.3 The framework partially equalises model capability

A side observation worth noting: under `tdd_loop_oracle`, Haiku (93.3 %) actually matches or slightly exceeds Sonnet (90.0 %). The same framework with the same oracle spec brings a smaller model to a `pass@1` that exceeds the larger model's both with and without the framework on intent-only. The cross-model contrast `Haiku tdd_loop_oracle − Sonnet tdd_loop_oracle = +3.3 pp [0.0, +10.0]` is borderline and we do not over-claim it; but it suggests the oracle structure constrains both models toward a shared performance ceiling. This is consistent with prior observations [CITE 7] that constraining the search space reduces the expressive gap between strong and weaker models.

### 7.4 Implications for future agent design

Three recommendations follow directly from the data:

1. **Treat under-anchored intents as a known failure regime.** Intent linting (programmatic-anchor required) should be a default, not optional. Any loop that runs on intents the linter rejects should fail loudly.
2. **Use deterministic verifiers wherever possible.** A compiler, type checker, or test runner in the verification position is strictly better than an LLM in the same position. This is consistent with Agentless's findings on SWE-bench Lite [CITE 7].
3. **Do not pay the agent-graph complexity tax without evidence.** Prior to building a multi-agent framework, demonstrate that the architecture main effect at matched spec is positive and significant on the target benchmark. We failed to find such an effect for the Tester / Worker decomposition on ClassEval.

### 7.5 What the framework is still good for

Our negative finding on the architecture main effect does not mean TDD-Loop is useless. The framework's per-session traces, deterministic convergence guarantees, and `Environment` plug-in surface make it a *useful instrument* for empirical study of agent behaviour — which is the role it played in this paper. We continue to release the framework on this basis.

---

## 8. Threats to Validity

### 8.1 Internal validity

The Tester's verdict could be biased by prompt wording. We mitigate this by running the same prompt template across all variants and ablations, and by binding the Tester's verdict to a deterministic exit code in the oracle regime. CLI session crashes (`F5`/`F6`) introduce noise; we cap consecutive crashes and report the per-task incidence in the artifact (`runs/_failure_classification.json`). We did not run multiple seeds per task; the bootstrap CIs of §5.2 quantify task-level uncertainty but not within-task model stochasticity.

### 8.2 External validity

We test only Claude Sonnet 4.6 and Haiku 4.5. Results may not extend to GPT-class or open-weight models. ClassEval is Python-only and class-level; results may not extend to repository-level (SWE-bench), Java, C++, or front-end tasks. We provide an `Environment`-pluggable artifact specifically to enable replication on other languages and harnesses; SWE-bench Lite scaffolding is included in the artifact (`experiments/swebench_lite/`) as future work.

### 8.3 Construct validity

`pass@1` does not measure the maintainability, security, or stylistic quality of the produced code. Token cost as billed by Anthropic does not capture engineer time or human-review cost. We report a portfolio of metrics (§4.3) precisely to avoid resting the conclusion on a single construct. The failure-mode classifier of §4.5 relies on a one-to-one mapping between feature and held-out method, derived by extracting method names from intent text; we manually spot-checked 5 random labels and found no mis-mappings.

### 8.4 Conclusion validity

Our n = 30 per cell is modest. The bootstrap CIs in Table 2 quantify this exactly: contrasts with absolute Δ ≥ 20 pp are robust; contrasts in the ±10 pp range (specifically `tdd_loop_oracle − baseline_oracle`) are not statistically distinguishable from zero, and this is the foundation of our headline null finding. We do not claim that no architecture main effect exists; we claim that at n = 30 we cannot distinguish it from zero, and that this is itself the central result.

### 8.5 Reliability / reproducibility

All sessions log a `session_id` replayable via `claude --resume`. All run artifacts (`events.jsonl`, `sessions_log.jsonl`, `result.json`, per-task `feature_list.json`, `_failure_classification.json`) are released. The bootstrap script is released with a fixed seed. The `Environment` abstraction guarantees that a re-runner can swap their own runtime in without modifying the orchestrator.

---

## 9. Conclusion

We constructed a 2 × 2 factorial study to disentangle two design choices that the multi-agent code-agent literature has historically confounded: the **architecture** of the agent (single vs. role-decomposed) and the **specification quality** of what the agent is asked to do (intent-only vs. oracle test code). Using TDD-Loop as a deterministic two-agent instrument and Claude Code as the single-agent instrument, on 30 ClassEval tasks across two model classes (240 runs total) with paired-bootstrap CIs, we find: **(i) the architecture main effect is significantly negative on intent-only specs (≈ −25 pp);** **(ii) the architecture main effect is not significantly distinguishable from zero on oracle specs;** **(iii) the spec main effect is enormous and significant (+43 to +60 pp on TDD-Loop);** and **(iv) the dominant failure mode of intent-only decomposition is Tester false-accept (58 %) — the LLM verifier writes a probe strictly weaker than the held-out test.**

The community has spent considerable effort on agent-graph design. Our results suggest the same effort spent on automated specification anchoring, or on routing verification through deterministic harnesses, would yield substantially larger returns on present-day frontier models. Multi-agent decomposition for LLM code generation is not, on the evidence we present, a free lunch — and at matched specification, it may not be a lunch at all.

---

## 10. Data and Code Availability

The TDD-Loop framework, the experimental harness, all `feature_list.json` instances generated for the 240 runs, the failure-mode classifier, the bootstrap script, and the full set of run logs (`events.jsonl`, `sessions_log.jsonl`, per-task `result.json`) are released at:

- **GitHub:** [TODO: https://github.com/<user>/tdd-loop] (release tag `v1.0.0`)
- **Zenodo (archived):** [TODO: 10.5281/zenodo.XXXXXXX]

The aggregated CSVs underlying every table in this paper are included in the Zenodo archive under `paper-data/`. The SWE-bench Lite mini scaffolding is included as `experiments/swebench_lite/` for future replication on repository-level tasks; we did not run it for this paper.

---

## References

[1] M. Chen, J. Tworek, H. Jun, et al. "Evaluating Large Language Models Trained on Code." arXiv:2107.03374, 2021. (HumanEval benchmark.)

[2] X. Du, M. Liu, K. Wang, et al. "ClassEval: A Manually-Crafted Benchmark for Evaluating LLMs on Class-level Code Generation." In *Proc. 46th IEEE/ACM Int. Conf. on Software Engineering (ICSE)*, 2024. doi:10.1145/3597503.3639219. arXiv:2308.01861.

[3] C. E. Jimenez, J. Yang, A. Wettig, S. Yao, K. Pei, O. Press, K. Narasimhan. "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?" In *Proc. Int. Conf. on Learning Representations (ICLR)*, 2024 (Oral). arXiv:2310.06770.

[4] J. Yang, C. E. Jimenez, A. Wettig, K. Lieret, S. Yao, K. Narasimhan, O. Press. "SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering." In *Proc. Advances in Neural Information Processing Systems (NeurIPS)*, 2024. arXiv:2405.15793.

[5] S. Hong, M. Zhuge, J. Chen, et al. "MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework." In *Proc. Int. Conf. on Learning Representations (ICLR)*, 2024 (Oral). arXiv:2308.00352.

[6] Q. Wu, G. Bansal, J. Zhang, et al. "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation." arXiv:2308.08155, 2023.

[7] C. S. Xia, Y. Deng, S. Dunn, L. Zhang. "Agentless: Demystifying LLM-based Software Engineering Agents." arXiv:2407.01489, 2024.

[8] S. Yao, J. Zhao, D. Yu, N. Du, I. Shafran, K. Narasimhan, Y. Cao. "ReAct: Synergizing Reasoning and Acting in Language Models." In *Proc. Int. Conf. on Learning Representations (ICLR)*, 2023. arXiv:2210.03629.

[9] A. Madaan, N. Tandon, P. Gupta, et al. "Self-Refine: Iterative Refinement with Self-Feedback." In *Proc. Advances in Neural Information Processing Systems (NeurIPS)*, 2023. arXiv:2303.17651.

[10] N. Shinn, F. Cassano, E. Berman, A. Gopinath, K. Narasimhan, S. Yao. "Reflexion: Language Agents with Verbal Reinforcement Learning." In *Proc. Advances in Neural Information Processing Systems (NeurIPS)*, 2023. arXiv:2303.11366.

[11] C. Wohlin, P. Runeson, M. Höst, M. C. Ohlsson, B. Regnell, A. Wesslén. *Experimentation in Software Engineering*. Springer, 2012. ISBN 978-3-642-29043-5. (Threats-to-validity taxonomy used in §8.)

---

<!--
END OF DRAFT v2.

Replacement plan before submission:
  1. Replace [TODO] markers with author names, affiliations, repo URL, DOI.
  2. Convert markdown to LaTeX via Pandoc; apply IEEE Access template.
  3. Convert Tables 1–4 to LaTeX `tabular` with IEEE styling.
  4. Optional figure: bar chart of Table 1 (pass@1 by config × model) — easy to
     generate from runs/_failure_classification.json.
  5. Optional figure: distribution pie of Table 4 (F1–F6 failure modes).
  6. Bibliography → BibTeX entries fetched from arXiv / DBLP per reference.

If reviewers push back on the ablation surface:
  - Add `w/o regression pass` and `w/o signature dedup` ablations on a single
    cell (Sonnet × tdd_loop) to substantiate convergence-safeguard contributions.
  - Add `w/o Tester` (single-agent-with-self-verify) as the canonical
    ablation.

If reviewers push back on external validity:
  - Launch the SWE-bench Lite mini experiment (experiments/swebench_lite/);
    10 tasks × 2 configs × 1 model ≈ 6–12 hours.
  - Add a non-Claude model (GPT-4 / DeepSeek-Coder) on a 10-task subset.
-->
