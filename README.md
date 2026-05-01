# tdd-loop-spec-quality-study

An empirical research artifact for studying LLM code-generation agents with a controlled 2x2 factorial design:

- **Architecture axis**: single-agent baseline vs two-agent TDD-Loop
- **Specification axis**: intent-only spec vs oracle (hidden-test-embedded) spec

The main finding of this study is that **spec quality dominates architecture** under matched conditions on ClassEval.

## Repository Overview

- `tdd_loop/`: deterministic two-agent framework (Tester + Worker + orchestrator)
- `experiments/classeval/`: benchmark harness, aggregation, bootstrap CI, failure classifier
- `experiments/classeval/runs/`: raw run artifacts used by the paper
- `docs/manuscript_draft.md`: manuscript draft
- `docs/findings_report.md`: analysis notes and result synthesis
- `examples/hello_world/`: runnable smoke test
- `prompts/`: agent prompts
- `environments/`: runtime adapters

## Quick Start

### 1) Requirements

- Python 3.10+
- Claude Code CLI installed and authenticated

### 2) Run aggregate table

```bash
python -m experiments.classeval.aggregate sonnet haiku
```

### 3) Recompute failure-mode labels

```bash
python -m experiments.classeval.classify_failures
```

### 4) Recompute paired-bootstrap confidence intervals

```bash
PYTHONIOENCODING=utf-8 python -m experiments.classeval.bootstrap_ci
```

## Reproducibility Notes

- Reported study size: 30 ClassEval tasks x 4 configs x 2 models = 240 runs.
- Per-task artifacts are stored under `experiments/classeval/runs/<model>/<config>/<task_id>/`.
- Core outputs include `result.json`, `solution.py`, `feature_list.json`, and `.tdd_loop_temp/` logs.

## Intended Citation

If you use this artifact, please cite the associated paper once published.

## License

MIT License. See `LICENSE`.
