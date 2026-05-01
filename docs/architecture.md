# Architecture notes

## Three-layer design

```
┌──────────────────────────────────────────────────────────────┐
│  Layer 1 — Spec (data)                                       │
│    feature_list.json: intent-only, status-machine per test   │
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

## Key invariants

- **Intent-only.** No test code is ever written into the feature list. This
  prevents the "blindly generated test" failure mode observed in early
  iterations of the framework (v1), where pre-written tests encoded wrong
  attribute names and misled the fixer agent for many iterations.
- **Disk facts, not self-reports.** When a session is interrupted, the
  replacement session is given a `git diff --name-only` listing and is
  instructed to re-read those files to determine state. It is *not* given
  the previous agent's claims about what it did.
- **Tester is read-only on source.** Any write by the Tester is a bug.
  The orchestrator does not enforce this mechanically — it relies on the
  prompt discipline and the fact that Worker is the fixer.
- **Worker does not verify.** Verification is the Tester's monopoly.
  A Worker that runs its own tests and emits pass/fail would create two
  verdicts per iteration and break the control-flow assumption.

## Convergence safeguards

The loop will terminate even on adversarial inputs:

| Mechanism | Trigger | Effect |
|---|---|---|
| `FEATURE_SKIP_THRESHOLD` | 5 attempts on same feature | Feature → skipped |
| `TEST_CONSECUTIVE_FAIL_THRESHOLD` | 3 fails on same test | Test → skipped |
| `TEST_REPEAT_REASON_THRESHOLD` | 2 fails with same normalised reason | Test → skipped (aggressive) |
| `CLI_CRASH_ABORT_THRESHOLD` | 5 consecutive CLI crashes | Loop aborts |
| `max_iterations` | run-level cap | Loop exits with `max_iterations_reached` |

The normalised-reason signature (`_normalize_reason`) strips timestamps,
coordinates, addresses, and literal numbers before hashing. Two failures
with the same structural cause but different timestamps collapse to one
signature; this is what makes the "same reason twice → skip" heuristic
responsive rather than brittle.

## Session persistence and replay

Every Tester / Worker invocation produces a Claude CLI `session_id` that
can be replayed with `claude --resume <session_id>`. The orchestrator
logs these to `sessions_log.jsonl` with cost, duration, and turn count.
This gives:

- Post-hoc debugging of individual agent decisions.
- Cost accounting per feature / per test.
- Reproducibility: rerunning the same feature list with the same models
  should produce comparable session counts and costs.

## What the Environment owns vs. the loop owns

| Concern | Owner |
|---|---|
| When to verify (iteration cadence) | Orchestrator |
| What counts as a pass | Tester (per prompt discipline) |
| How to probe at runtime | Environment (via `capabilities` doc + env vars) |
| Bringing up/tearing down runtime state | Environment |
| Persistent state across iterations (status, logs) | Orchestrator |
| Per-test setup/teardown | Environment `notify_pre_verify` |
| Reacting to source edits (hot-reload etc.) | Environment `notify_post_worker` |

Keeping this split clean is load-bearing for the paper's generalisability
claim.
