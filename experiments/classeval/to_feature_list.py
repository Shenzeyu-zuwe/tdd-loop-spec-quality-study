# -*- coding: utf-8 -*-
"""Convert a ClassEval task into a feature_list.json with RUNTIME intents.

Prior versions generated "method exists with this signature" and "behaviour
matches docstring" intents, which the Tester answered via pure code
review — producing false greens when the code looks right but misbehaves
on held-out tests.

This version:
  1. Parses docstring doctest blocks (>>> call → expected output) into
     concrete runtime check specs.
  2. Emits one test per doctest example, with an intent that describes the
     exact script to run and the exact stdout to match.
  3. For methods without doctests (~6% of ClassEval), emits a single intent
     that requires the Tester to write and execute at least one concrete
     runtime check, explicitly forbidding static code review as the basis
     of a pass.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


# ── Doctest parsing ────────────────────────────────────────────────

def _extract_doctest_groups(docstring: str) -> list[dict]:
    """Parse doctest blocks into {setup, check_expr, expected} groups.

    Each group represents one concrete runtime assertion:
      setup:     list of Python statements establishing state (no expected output)
      check_expr: the Python expression whose value is printed
      expected:  the exact expected stdout (stripped)
    Consecutive `>>>` lines accumulate into setup; the first `>>>` whose
    following non-`>>>` lines are non-empty becomes the check_expr.
    """
    lines = docstring.split("\n")
    groups: list[dict] = []
    pending_setup: list[str] = []

    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped.startswith(">>> "):
            i += 1
            continue

        code = stripped[4:]
        # Continuation lines (PEP 257: ... )
        j = i + 1
        while j < len(lines) and lines[j].strip().startswith("... "):
            code += "\n" + lines[j].strip()[4:]
            j += 1

        # Collect following non->>> non-... lines as expected output,
        # until the next >>> or end / blank separator.
        expected_lines: list[str] = []
        k = j
        while k < len(lines):
            s = lines[k].strip()
            if s.startswith(">>>") or s.startswith("..."):
                break
            if not s:
                # Blank line ends the expected block.
                break
            expected_lines.append(s)
            k += 1

        expected = "\n".join(expected_lines).strip()
        if expected:
            groups.append({
                "setup": list(pending_setup),
                "check_expr": code,
                "expected": expected,
            })
            pending_setup = []
        else:
            pending_setup.append(code)

        i = k

    return groups


def _build_runtime_script(import_statement: str, class_name: str,
                           group: dict) -> str:
    """Build a self-contained Python script that runs the check and prints
    the check expression's value."""
    setup_block = "\n".join(group["setup"])
    check = group["check_expr"]

    # If the check is already a call ending with the object itself (not print),
    # wrap in print(). Detect 'print(' prefix — if so, keep as-is.
    if check.strip().startswith("print(") or "=" in check.split("#", 1)[0]:
        exec_line = check
    else:
        exec_line = f"print({check})"

    script = (
        "import sys\n"
        "sys.path.insert(0, '.')\n"
        f"{import_statement.strip()}\n"
        f"from solution import {class_name}\n"
        f"{setup_block}\n"
        f"{exec_line}\n"
    )
    return script


# ── Intent authoring ───────────────────────────────────────────────

def _authoritative_runtime_intent(class_name: str, method_name: str,
                                    import_statement: str, group: dict) -> str:
    """One concrete, fully executable intent. No room for 'looks right'."""
    script = _build_runtime_script(import_statement, class_name, group)
    expected = group["expected"]
    return (
        f"RUNTIME CHECK for `{class_name}.{method_name}`.\n"
        f"\n"
        f"Write the following Python code to a temp file (e.g. `_t.py`) in the "
        f"project root and run `python _t.py` via the Bash tool. Capture its "
        f"stdout. The stdout, stripped of trailing whitespace, must equal the "
        f"expected output exactly.\n"
        f"\n"
        f"Script:\n"
        f"```python\n{script}```\n"
        f"\n"
        f"Expected stdout:\n"
        f"```\n{expected}\n```\n"
        f"\n"
        f"If the script raises an exception, stdout diverges, or you do not "
        f"actually execute it, the test is FAILED (not passed). Do not infer "
        f"behaviour from reading code."
    )


def _fallback_runtime_intent(class_name: str, method_name: str,
                              docstring: str) -> str:
    """When no doctest is available, instruct the Tester to author its own
    runtime test. Still demands actual execution."""
    return (
        f"RUNTIME CHECK for `{class_name}.{method_name}` (no doctest examples "
        f"in the spec — you must design the test).\n"
        f"\n"
        f"Read the docstring below carefully. Design at least two concrete "
        f"runtime calls that exercise the behaviour it describes. Write them "
        f"into a temp Python script in the project root (import the class via "
        f"`from solution import {class_name}`). Execute it with "
        f"`python <temp>.py` via the Bash tool. Verify that:\n"
        f"  1. The script runs without exception.\n"
        f"  2. For each call, the observed return value matches what the "
        f"docstring says it should be.\n"
        f"\n"
        f"A test is only PASSED if you executed the script and observed "
        f"correct behaviour. Code review alone is NOT acceptable as evidence.\n"
        f"\n"
        f"Docstring contract:\n{docstring}"
    )


# ── Public API ─────────────────────────────────────────────────────

def _extract_docstring(method_description: str) -> str:
    m = re.search(r'"""(.*?)"""', method_description, re.DOTALL)
    return m.group(1).strip() if m else method_description


def _clean_sig(method_description: str) -> str:
    m = re.search(r"def\s+(\w+\s*\([^)]*\))", method_description)
    return m.group(1) if m else "(unknown)"


def build_feature_list(task: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    class_name = task["class_name"]
    import_stmt = task["import_statement"]
    methods = task["methods_info"]

    features = []
    for i, mi in enumerate(methods, 1):
        mname = mi["method_name"]
        sig = _clean_sig(mi["method_description"])
        docstring = _extract_docstring(mi["method_description"])

        groups = _extract_doctest_groups(docstring)

        test_cases = []
        if groups:
            for j, g in enumerate(groups, 1):
                test_cases.append({
                    "id": f"T-{i:03d}-{j:02d}",
                    "intent": _authoritative_runtime_intent(
                        class_name, mname, import_stmt, g,
                    ),
                    "status": "pending",
                })
        else:
            test_cases.append({
                "id": f"T-{i:03d}-01",
                "intent": _fallback_runtime_intent(class_name, mname, docstring),
                "status": "pending",
            })

        features.append({
            "id": f"F-{i:03d}",
            "intent": (
                f"Method `{sig}` on class `{class_name}` executes correctly "
                f"at runtime against its docstring's concrete examples."
            ),
            "status": "pending",
            "dependencies": [],
            "test_cases": test_cases,
        })

    fl = {
        "change_name": task["task_id"],
        "class_name": class_name,
        "class_description": task["class_description"],
        "import_statement": import_stmt,
        "features": features,
        "summary": {},
    }

    out_path = out_dir / "feature_list.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(fl, f, ensure_ascii=False, indent=2)
    return out_path


# ── Oracle ablation: pre-written tests as intents ─────────────────

def _oracle_runtime_intent(class_name: str, method_name: str,
                            import_statement: str, test_class: str,
                            test_code: str) -> str:
    """Intent that tells the Tester to execute the *actual* hidden ClassEval
    unittest. Used by the oracle ablation arm to isolate whether the bug is
    in (a) the intent-only spec or (b) the dual-agent loop itself.

    The Tester's job collapses to: write a runner script, execute it, parse
    unittest's output, return PASS/FAIL. No interpretation of intent."""
    runner = (
        "import sys, unittest\n"
        "sys.path.insert(0, '.')\n"
        f"{import_statement.strip()}\n"
        f"from solution import {class_name}\n"
        "\n"
        f"{test_code.strip()}\n"
        "\n"
        "if __name__ == '__main__':\n"
        f"    suite = unittest.TestLoader().loadTestsFromTestCase({test_class})\n"
        "    runner = unittest.TextTestRunner(verbosity=2)\n"
        "    result = runner.run(suite)\n"
        "    sys.exit(0 if result.wasSuccessful() else 1)\n"
    )
    return (
        f"ORACLE TEST RUN for `{class_name}.{method_name}`.\n"
        f"\n"
        f"Write the following Python code to a temp file (e.g. `_oracle_{method_name}.py`) "
        f"in the project root and execute `python _oracle_{method_name}.py` via the Bash "
        f"tool. The script runs the hidden unit tests for this method.\n"
        f"\n"
        f"PASS criteria: process exits with code 0 AND unittest reports `OK` "
        f"(no failures, no errors).\n"
        f"FAIL criteria: any failure, error, exception, or non-zero exit. "
        f"Do NOT modify the test code. Do NOT infer the result without "
        f"actually executing the script.\n"
        f"\n"
        f"Script:\n"
        f"```python\n{runner}```\n"
    )


def build_feature_list_oracle(task: dict, out_dir: Path) -> Path:
    """Oracle ablation: each method's feature has a single test case whose
    intent embeds the actual ClassEval hidden unittest for that method."""
    out_dir.mkdir(parents=True, exist_ok=True)
    class_name = task["class_name"]
    import_stmt = task["import_statement"]
    methods = task["methods_info"]

    features = []
    for i, mi in enumerate(methods, 1):
        mname = mi["method_name"]
        sig = _clean_sig(mi["method_description"])
        test_class = mi.get("test_class", "")
        test_code = mi.get("test_code", "")
        if not (test_class and test_code):
            # No hidden test wired up — fall back to intent-only behaviour.
            docstring = _extract_docstring(mi["method_description"])
            test_cases = [{
                "id": f"T-{i:03d}-01",
                "intent": _fallback_runtime_intent(class_name, mname, docstring),
                "status": "pending",
            }]
        else:
            test_cases = [{
                "id": f"T-{i:03d}-01",
                "intent": _oracle_runtime_intent(
                    class_name, mname, import_stmt, test_class, test_code,
                ),
                "status": "pending",
            }]

        features.append({
            "id": f"F-{i:03d}",
            "intent": (
                f"Method `{sig}` on class `{class_name}` passes its hidden "
                f"unit-test suite (oracle ablation arm)."
            ),
            "status": "pending",
            "dependencies": [],
            "test_cases": test_cases,
        })

    fl = {
        "change_name": task["task_id"],
        "class_name": class_name,
        "class_description": task["class_description"],
        "import_statement": import_stmt,
        "features": features,
        "summary": {},
    }

    out_path = out_dir / "feature_list.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(fl, f, ensure_ascii=False, indent=2)
    return out_path


def build_spec_md(task: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "SPEC.md"
    lines = [
        f"# {task['task_id']} — {task['class_name']}",
        "",
        "## Class description",
        "```",
        task["class_description"].strip(),
        "```",
        "",
        "## Required imports (prepend to solution.py)",
        "```python",
        task["import_statement"].strip(),
        "```",
        "",
        "## Skeleton (to implement)",
        "```python",
        task["skeleton"].strip(),
        "```",
        "",
        "## Target file",
        "`solution.py` — write the completed class here. Do **not** modify",
        "any other file in the project root.",
        "",
        "## Verification discipline",
        "Every test intent in feature_list.json is a **RUNTIME CHECK**. The",
        "Tester must write a temp Python script, execute it via the Bash",
        "tool, and compare actual stdout to expected. Code review alone is",
        "never sufficient.",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path
