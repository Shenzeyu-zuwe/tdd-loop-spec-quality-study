# -*- coding: utf-8 -*-
"""ClassEval dataset loader.

One ClassEval record shape:
    task_id          str    e.g. "ClassEval_0"
    class_name       str
    class_description str   docstring block
    skeleton         str    class skeleton w/ method docstrings (bodies to fill)
    import_statement str    prelude imports the class needs
    methods_info     list   [{method_name, method_description, test_class, test_code}]
    test             str    all tests concatenated (unittest)
    test_classes     list   per-method test source blocks (strings)
    solution_code    str    reference solution (not used by runners, only optional sanity)
"""

from __future__ import annotations

import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent / "data" / "ClassEval_data.json"


def _normalize(task: dict) -> dict:
    """Ensure import_statement is a string (it's a list of lines in the raw json)."""
    imp = task.get("import_statement", "")
    if isinstance(imp, list):
        task["import_statement"] = "\n".join(imp)
    return task


def load_all() -> list[dict]:
    with open(DATA_PATH, encoding="utf-8") as f:
        return [_normalize(t) for t in json.load(f)]


def load_task(task_id: str) -> dict:
    for t in load_all():
        if t["task_id"] == task_id:
            return t
    raise KeyError(task_id)


def task_ids() -> list[str]:
    return [t["task_id"] for t in load_all()]


def pick_subset(n: int, offset: int = 0, seed: int | None = None) -> list[dict]:
    """Deterministic subset selection.

    seed=None: contiguous slice starting at offset (fast debug).
    seed=int:  random subset with fixed seed (used for representative sampling).
    """
    tasks = load_all()
    if seed is None:
        return tasks[offset:offset + n]
    import random
    rng = random.Random(seed)
    return rng.sample(tasks, min(n, len(tasks)))
