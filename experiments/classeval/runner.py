# -*- coding: utf-8 -*-
"""ClassEval runner — orchestrates baseline and TDD-Loop runs.

Usage:
    python -m experiments.classeval.runner \
        --configs baseline,tdd_loop \
        --models sonnet \
        --n 3 \
        --offset 0

Each (task, config, model) triple produces one run under
  experiments/classeval/runs/<model>/<config>/<task_id>/

with at least:
  - solution.py          (generated class)
  - result.json          (status, duration, cost, evaluation outcome)
  - raw_response.txt     (baseline only — full model response)
  - .tdd_loop_temp/*     (tdd_loop only — the orchestrator's logs)
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
import time
from pathlib import Path

# Package-path bootstrap so both `python -m experiments.classeval.runner`
# and `python experiments/classeval/runner.py` work.
_PKG_ROOT = Path(__file__).resolve().parents[2]
if str(_PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(_PKG_ROOT))

from experiments.classeval import loader, to_feature_list  # noqa: E402
from experiments.classeval.baseline_runner import run_baseline  # noqa: E402
from experiments.classeval.evaluator import evaluate  # noqa: E402

logger = logging.getLogger("classeval_runner")

RUNS_DIR = Path(__file__).resolve().parent / "runs"


def _setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def _work_dir(model: str, config: str, task_id: str) -> Path:
    d = RUNS_DIR / model / config / task_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_result(path: Path, obj: dict):
    with open(path / "result.json", "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


# ── Config: baseline ────────────────────────────────────────────────

def run_config_baseline(task: dict, model: str, variant: str = "intent") -> dict:
    cfg_name = "baseline" if variant == "intent" else f"baseline_{variant}"
    work = _work_dir(model, cfg_name, task["task_id"])
    t0 = time.time()
    meta = run_baseline(task, work, model=model, variant=variant)
    wall = time.time() - t0

    result = {
        "task_id": task["task_id"], "class_name": task["class_name"],
        "config": cfg_name, "model": model,
        "gen_status": meta["status"],
        "gen_duration_s": meta["duration_s"],
        "gen_cost_usd": meta["cost_usd"],
        "gen_session_id": meta["session_id"],
        "wall_time_s": round(wall, 1),
        "eval": None,
        "error": meta.get("error", ""),
    }

    if meta["status"] == "ok" and meta["solution_path"]:
        eval_result = evaluate(task, Path(meta["solution_path"]))
        result["eval"] = eval_result
    _write_result(work, result)
    return result


# ── Config: tdd_loop ────────────────────────────────────────────────

def run_config_tdd_loop(task: dict, model: str, max_iter: int = 15,
                          variant: str = "intent") -> dict:
    """Run the TDD-Loop orchestrator on this task.

    variant:
      - "intent" (default): test cases derived from docstring doctests
        (the intent-only spec arm)
      - "oracle": test cases embed the actual ClassEval hidden unittest
        (ablation arm — isolates whether the bug is in spec source or loop)

    Steps:
      1. Write feature_list.json + SPEC.md + solution.py seed (empty) into the work dir.
      2. Launch `python -m tdd_loop.run <fl> --project-dir <work> --environment null`
         as a subprocess. (Matches how users invoke it; keeps process isolation.)
      3. After it exits, evaluate the resulting solution.py.
    """
    cfg_name = "tdd_loop" if variant == "intent" else f"tdd_loop_{variant}"
    work = _work_dir(model, cfg_name, task["task_id"])

    # 1. Artifacts
    if variant == "oracle":
        fl_path = to_feature_list.build_feature_list_oracle(task, work)
    else:
        fl_path = to_feature_list.build_feature_list(task, work)
    spec_path = to_feature_list.build_spec_md(task, work)
    solution_path = work / "solution.py"
    if not solution_path.exists():
        # seed with imports + class skeleton; the Worker will fill in bodies.
        seed = (
            task["import_statement"].rstrip() + "\n\n"
            + task["skeleton"].rstrip() + "\n"
        )
        solution_path.write_text(seed, encoding="utf-8")

    # git init so tdd_loop's diff-based heuristics work.
    if not (work / ".git").exists():
        subprocess.run(["git", "init", "-q"], cwd=str(work), check=False)
        subprocess.run(["git", "add", "-A"], cwd=str(work), check=False)
        subprocess.run(["git", "commit", "-q", "-m", "baseline", "--allow-empty"],
                        cwd=str(work), check=False,
                        env={"GIT_AUTHOR_NAME": "classeval", "GIT_AUTHOR_EMAIL": "ce@local",
                             "GIT_COMMITTER_NAME": "classeval", "GIT_COMMITTER_EMAIL": "ce@local",
                             "PATH": ""})  # tight env

    # 2. Launch the orchestrator.
    cmd = [
        sys.executable, "-m", "tdd_loop.run",
        str(fl_path),
        "--project-dir", str(work),
        "--spec", str(spec_path),
        "--environment", "python_local",
        "--max-iter", str(max_iter),
    ]
    if model and model != "default":
        cmd.extend(["--model", model])

    t0 = time.time()
    try:
        r = subprocess.run(
            cmd, cwd=str(_PKG_ROOT),
            capture_output=True, encoding="utf-8", errors="replace",
            timeout=max_iter * 60 * 3,  # rough wall budget
        )
    except subprocess.TimeoutExpired:
        r = None
    wall = time.time() - t0

    # 3. Collect loop artefacts.
    temp_dir = work / ".tdd_loop_temp"
    sessions_path = temp_dir / "sessions_log.jsonl"
    total_cost = 0
    session_count = 0
    if sessions_path.exists():
        for line in sessions_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                total_cost += rec.get("cost_usd", 0) or 0
                session_count += 1
            except json.JSONDecodeError:
                pass

    iterations = 0
    fl_state_path = work / "feature_list.json"
    fl_summary = {}
    if fl_state_path.exists():
        try:
            fl_json = json.loads(fl_state_path.read_text(encoding="utf-8"))
            fl_summary = fl_json.get("summary", {})
        except json.JSONDecodeError:
            pass

    # Parse iteration count from events.jsonl tail.
    events_path = temp_dir / "events.jsonl"
    if events_path.exists():
        try:
            for line in reversed(events_path.read_text(encoding="utf-8").splitlines()):
                try:
                    ev = json.loads(line)
                    if ev.get("kind") == "run_end":
                        iterations = ev.get("detail", {}).get("iterations", 0)
                        break
                except json.JSONDecodeError:
                    continue
        except OSError:
            pass

    result = {
        "task_id": task["task_id"], "class_name": task["class_name"],
        "config": cfg_name, "model": model,
        "gen_status": "timeout" if r is None else ("ok" if r.returncode == 0 else "error"),
        "gen_duration_s": round(wall, 1),
        "gen_cost_usd": round(total_cost, 6),
        "gen_session_count": session_count,
        "gen_iterations": iterations,
        "fl_summary": fl_summary,
        "wall_time_s": round(wall, 1),
        "eval": None,
        "error": "" if r is not None and r.returncode == 0 else (
            "timeout" if r is None else (r.stderr or r.stdout or "")[-600:]
        ),
    }

    if solution_path.exists():
        eval_result = evaluate(task, solution_path)
        result["eval"] = eval_result

    _write_result(work, result)
    return result


# ── Main ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="ClassEval runner for TDD-Loop vs baseline")
    parser.add_argument("--configs", default="baseline,tdd_loop",
                        help="Comma-list of configs to run (baseline,tdd_loop)")
    parser.add_argument("--models", default="sonnet",
                        help="Comma-list of model names, e.g. sonnet,opus,haiku")
    parser.add_argument("--n", type=int, default=3, help="Number of tasks to run")
    parser.add_argument("--offset", type=int, default=0, help="Task offset (contiguous slice)")
    parser.add_argument("--seed", type=int, default=None,
                        help="If set, use a random subset with this seed instead of contiguous")
    parser.add_argument("--max-iter", type=int, default=15,
                        help="Max TDD-Loop iterations per task (default: 15)")
    parser.add_argument("--task-ids", default=None,
                        help="Comma-list of specific task_ids; overrides --n/--offset")
    args = parser.parse_args()

    _setup_logging()

    configs = [c.strip() for c in args.configs.split(",") if c.strip()]
    models = [m.strip() for m in args.models.split(",") if m.strip()]

    if args.task_ids:
        wanted = set(s.strip() for s in args.task_ids.split(",") if s.strip())
        tasks = [t for t in loader.load_all() if t["task_id"] in wanted]
    else:
        tasks = loader.pick_subset(args.n, offset=args.offset, seed=args.seed)

    logger.info(f"Tasks: {[t['task_id'] for t in tasks]}")
    logger.info(f"Configs: {configs}  Models: {models}")
    logger.info(f"Total runs: {len(tasks) * len(configs) * len(models)}")

    summary_rows = []
    for model in models:
        for task in tasks:
            for cfg in configs:
                logger.info(f"\n=== {task['task_id']}  cfg={cfg}  model={model} ===")
                t0 = time.time()
                try:
                    if cfg == "baseline":
                        res = run_config_baseline(task, model, variant="intent")
                    elif cfg == "baseline_oracle":
                        res = run_config_baseline(task, model, variant="oracle")
                    elif cfg == "tdd_loop":
                        res = run_config_tdd_loop(task, model, max_iter=args.max_iter, variant="intent")
                    elif cfg == "tdd_loop_oracle":
                        res = run_config_tdd_loop(task, model, max_iter=args.max_iter, variant="oracle")
                    else:
                        logger.warning(f"Unknown config: {cfg}")
                        continue
                except Exception as e:
                    logger.exception(f"Run crashed: {e}")
                    res = {"task_id": task["task_id"], "config": cfg, "model": model,
                            "error": str(e)[:500], "eval": None}
                elapsed = time.time() - t0
                ev = res.get("eval") or {}
                logger.info(
                    f"  → gen_status={res.get('gen_status')} "
                    f"class_passed={ev.get('class_passed')} "
                    f"method={ev.get('method_pass_count')}/{ev.get('method_total')} "
                    f"cost=${res.get('gen_cost_usd', 0):.4f} "
                    f"wall={elapsed:.1f}s"
                )
                summary_rows.append(res)

    # Write aggregate summary.
    summary_path = RUNS_DIR / f"summary_{int(time.time())}.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "configs": configs, "models": models,
            "tasks": [t["task_id"] for t in tasks],
            "results": summary_rows,
        }, f, ensure_ascii=False, indent=2)
    logger.info(f"\nSummary: {summary_path}")

    # Quick table to stdout.
    logger.info(f"\n{'=' * 70}")
    for model in models:
        for cfg in configs:
            rows = [r for r in summary_rows if r.get("model") == model and r.get("config") == cfg]
            passed = sum(1 for r in rows if (r.get("eval") or {}).get("class_passed"))
            total = len(rows)
            cost = sum(r.get("gen_cost_usd", 0) or 0 for r in rows)
            pct = (100.0 * passed / total) if total else 0.0
            logger.info(f"  [{model:10}] {cfg:10} class-pass@1: {passed}/{total} ({pct:.1f}%)  total_cost=${cost:.4f}")


if __name__ == "__main__":
    main()
