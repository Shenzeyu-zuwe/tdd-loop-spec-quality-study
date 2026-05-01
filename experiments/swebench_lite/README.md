# SWE-bench Lite mini harness

Goal: validate the **task-complexity crossover** hypothesis from the
ClassEval results. On ClassEval (class-level, single-file) the intent-only
TDD-Loop loses to the baseline by ~25 pp. The hypothesis is that on
repository-level tasks the gap narrows or reverses, because the per-task
verification overhead is amortised against a higher first-shot error rate.

## What this directory contains

```
swebench_lite/
├── README.md            this file
├── loader.py            fetch 10 mini-subset tasks from HuggingFace SWE-bench_Lite
├── to_feature_list.py   convert (problem_statement, FAIL_TO_PASS) → feature_list.json
├── env_repo.py          Environment adapter: per-task git checkout + pytest harness
├── runner.py            Orchestrator: baseline / tdd_loop / oracle variants
├── evaluator.py         Apply candidate patch, run target tests, record FAIL_TO_PASS / PASS_TO_PASS
└── runs/                output (created on first run)
```

## Pre-flight (one-time setup, ~10 min)

```bash
# 1. Install SWE-bench evaluation dependencies
pip install swebench datasets

# 2. (Recommended) Docker is the SWE-bench official harness. We ship a
#    docker-less "venv-per-task" fallback that works for the 10-task
#    mini-subset of pure-Python repos chosen by loader.py.
#    If you want full SWE-bench Lite (300 tasks) eventually, install Docker.

# 3. Sanity check the loader
python -m experiments.swebench_lite.loader --list
```

## Launch the 10-task mini-run

```bash
# Both configs, both models — ~6 hours total on a typical workstation
python -m experiments.swebench_lite.runner \
    --configs baseline,tdd_loop \
    --models sonnet \
    --n 10
```

Each task produces:
```
runs/<model>/<config>/<task_id>/
├── feature_list.json    (tdd_loop only — intent-only spec)
├── patch.diff           (the candidate patch produced by the run)
├── result.json          (status, cost, duration, FAIL_TO_PASS / PASS_TO_PASS counts)
└── .tdd_loop_temp/      (tdd_loop only — orchestrator logs)
```

Aggregate:
```bash
python -m experiments.swebench_lite.aggregate sonnet
```

## What's stubbed and needs a decision

The 10-task subset is curated for being **runnable without Docker** — pure-Python repos
with `pip install -e .` working out of the box (`flask`, `requests`, `pytest`, `sqlfluff`,
`marshmallow` reference instances). If you want the canonical SWE-bench Lite
ecosystem (which includes packages requiring system deps), use the Docker
harness via `swebench.harness.run_evaluation`.

The runner imports the official `swebench` package's evaluation function for the
PASS_TO_PASS / FAIL_TO_PASS gate. If that package is unavailable, evaluator.py
falls back to a hand-rolled pytest invocation that matches the gate semantics
but does not reproduce SWE-bench's exact retry/cleanup logic.

## What insight this should validate

If the headline ClassEval finding ("decomposition harms with weak spec") is
**universal**, we expect:
- `tdd_loop − baseline` on SWE-bench Lite mini ≈ similar or larger negative gap

If the **task-complexity crossover** hypothesis holds, we expect:
- `tdd_loop − baseline` on SWE-bench Lite mini → smaller negative gap, ≈ 0, or positive

Either result is publishable. The first sharpens "spec is the bottleneck";
the second introduces a complexity-dependent boundary on the claim.
