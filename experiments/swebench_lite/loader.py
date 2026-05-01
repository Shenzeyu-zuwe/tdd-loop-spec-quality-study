# -*- coding: utf-8 -*-
"""SWE-bench Lite mini-subset loader.

Pulls a curated 10-task subset from the official `princeton-nlp/SWE-bench_Lite`
HuggingFace dataset, biased toward repos that build cleanly with `pip install -e .`
in a fresh venv (no system-level apt packages). This makes the docker-less
fallback evaluator viable for the 10-task pilot.

Curation criteria:
- repo in {flask, requests, pytest, sqlfluff, marshmallow, pylint, astroid, scrapy}
- problem_statement length between 200 and 4000 chars (avoids degenerate / overlong)
- single FAIL_TO_PASS test (cleaner intent-only signal)
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

# 10 instance_ids hand-picked for the mini-pilot. Stable IDs.
# Curation rationale documented in README.md. If any are unreachable, replace
# with adjacent IDs from the same repo at the same commit family.
MINI_SUBSET_INSTANCE_IDS = [
    "pallets__flask-5014",
    "pallets__flask-4992",
    "psf__requests-1142",
    "psf__requests-2317",
    "pytest-dev__pytest-5103",
    "pytest-dev__pytest-7373",
    "marshmallow-code__marshmallow-1359",
    "marshmallow-code__marshmallow-1867",
    "sqlfluff__sqlfluff-1517",
    "sqlfluff__sqlfluff-2419",
]


def load_subset() -> list[dict]:
    """Load the 10 mini-subset tasks from the HuggingFace dataset.

    Returns a list of dicts with keys:
      instance_id, repo, base_commit, problem_statement, FAIL_TO_PASS,
      PASS_TO_PASS, patch (gold), test_patch
    """
    try:
        from datasets import load_dataset
    except ImportError as e:
        raise SystemExit(
            "datasets package not installed; run `pip install datasets swebench`"
        ) from e

    ds = load_dataset("princeton-nlp/SWE-bench_Lite", split="test")
    wanted = set(MINI_SUBSET_INSTANCE_IDS)
    rows = [r for r in ds if r["instance_id"] in wanted]
    rows.sort(key=lambda r: MINI_SUBSET_INSTANCE_IDS.index(r["instance_id"]))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="Just print the 10 instance ids and exit (no network).")
    ap.add_argument("--dump", type=Path, help="Write fetched tasks to a JSON file.")
    args = ap.parse_args()

    if args.list:
        for tid in MINI_SUBSET_INSTANCE_IDS:
            print(tid)
        return

    rows = load_subset()
    print(f"Loaded {len(rows)} tasks.")
    for r in rows:
        ps = r.get("problem_statement") or ""
        print(f"  {r['instance_id']:<40} repo={r['repo']:<40} ps_len={len(ps)}")

    if args.dump:
        args.dump.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nWrote {args.dump}")


if __name__ == "__main__":
    main()
