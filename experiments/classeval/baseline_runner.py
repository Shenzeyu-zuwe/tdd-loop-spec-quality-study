# -*- coding: utf-8 -*-
"""Raw Claude CLI baseline — single-shot class generation.

One subprocess call to `claude -p` gives the model the skeleton + docstrings
and asks for a complete implementation. No iteration, no tester, no
verification. This is the simplest honest baseline: "what does the CLI do
if you just ask it to implement the class?"

Output: solution.py at the given workspace path, plus a JSON metadata
record (session_id, cost_usd, duration_ms).
"""

from __future__ import annotations

import json
import re
import subprocess
import time
from pathlib import Path

BASELINE_PROMPT = """\
You are given a Python class skeleton with method docstrings. Your job is
to implement every method so the class satisfies the behaviour described
in the docstrings.

## Required imports (keep these at the top of your output)
```python
{imports}
```

## Class skeleton
```python
{skeleton}
```

## Instructions
- Write a complete, self-contained Python file that defines the class.
- Keep all method signatures and class/method names exactly as in the skeleton.
- Include the required imports above.
- Do **not** include tests, example usage, or commentary — just the class.
- Output your solution as one ```python fenced block. Nothing outside the block.
"""


BASELINE_ORACLE_PROMPT = """\
You are given a Python class skeleton with method docstrings AND the unit
tests that will be used to evaluate your implementation. Your job is to
implement every method so the class passes every test.

## Required imports (keep these at the top of your output)
```python
{imports}
```

## Class skeleton
```python
{skeleton}
```

## Hidden tests that will be used to grade your implementation
```python
{tests}
```

## Instructions
- Write a complete, self-contained Python file that defines the class.
- Keep all method signatures and class/method names exactly as in the skeleton.
- Include the required imports above.
- Your code must make every assertion in the tests above pass.
- Do **not** include tests, example usage, or commentary — just the class.
- Output your solution as one ```python fenced block. Nothing outside the block.
"""


def _extract_python_block(text: str) -> str:
    """Extract the first ```python ... ``` block; fall back to the whole text."""
    m = re.search(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text.strip()


def run_baseline(task: dict, out_dir: Path, model: str = "sonnet",
                  timeout: int = 600, variant: str = "intent") -> dict:
    """Run a single baseline generation. Returns a metadata dict.

    variant:
      - "intent" (default): docstring-only prompt. Tests are HIDDEN.
      - "oracle": docstring + actual hidden test_code in the prompt.
        Disambiguates how much of dual-agent oracle's gain is framework
        vs information access (test visibility).
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    config_name = "baseline" if variant == "intent" else f"baseline_{variant}"
    if variant == "oracle":
        # Concatenate every method's hidden test_code. Identical body to
        # what tdd_loop_oracle embeds, so test visibility is matched.
        test_blocks = []
        for mi in task.get("methods_info", []):
            tc = mi.get("test_code", "").strip()
            if tc:
                test_blocks.append(tc)
        tests_str = "\n\n".join(test_blocks) if test_blocks else "# (no test_code in dataset)"
        prompt = BASELINE_ORACLE_PROMPT.format(
            imports=task["import_statement"].strip(),
            skeleton=task["skeleton"].strip(),
            tests=tests_str,
        )
    else:
        prompt = BASELINE_PROMPT.format(
            imports=task["import_statement"].strip(),
            skeleton=task["skeleton"].strip(),
        )
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "json",
        "--tools", "default",
        "--permission-mode", "bypassPermissions",
        "--max-turns", "10",
    ]
    if model and model != "default":
        cmd.extend(["--model", model])

    t0 = time.time()
    try:
        r = subprocess.run(
            cmd, cwd=str(out_dir),
            capture_output=True, encoding="utf-8", errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {
            "task_id": task["task_id"], "config": config_name, "model": model,
            "status": "timeout", "duration_s": timeout,
            "solution_path": None, "session_id": None,
            "cost_usd": 0, "error": "timeout",
        }
    duration_s = time.time() - t0

    stdout = r.stdout or ""
    stderr = r.stderr or ""

    session_id = None
    cost_usd = 0
    output_text = stdout
    try:
        payload = json.loads(stdout)
        if isinstance(payload, dict):
            session_id = payload.get("session_id")
            cost_usd = payload.get("total_cost_usd", 0)
            output_text = payload.get("result", stdout)
    except json.JSONDecodeError:
        pass

    if r.returncode != 0:
        return {
            "task_id": task["task_id"], "config": config_name, "model": model,
            "status": "error", "duration_s": round(duration_s, 1),
            "solution_path": None, "session_id": session_id,
            "cost_usd": cost_usd,
            "error": (stderr or stdout)[:500],
        }

    code = _extract_python_block(output_text)
    solution_path = out_dir / "solution.py"
    solution_path.write_text(code, encoding="utf-8")

    (out_dir / "raw_response.txt").write_text(output_text, encoding="utf-8")

    return {
        "task_id": task["task_id"], "config": "baseline", "model": model,
        "status": "ok", "duration_s": round(duration_s, 1),
        "solution_path": str(solution_path),
        "session_id": session_id, "cost_usd": cost_usd,
        "error": "",
    }
