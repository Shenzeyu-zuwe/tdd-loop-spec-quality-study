# -*- coding: utf-8 -*-
"""ClassEval evaluator.

Given a generated solution.py and a ClassEval task record, run the
per-method test classes in an isolated subprocess and report pass/fail at
both class level and method level.

Scoring follows ClassEval's official convention:
  - method pass = all assertions in that method's test class pass
  - class pass  = every method's test class passes

We invoke a fresh Python interpreter per task so import errors or sys.path
pollution in one solution can't leak into another.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path


def _evaluator_script() -> str:
    """Stand-alone evaluator executed in a subprocess. Reads stdin for
    {solution_path, imports, test_classes, class_name}, writes JSON result
    to stdout.

    Using a subprocess keeps the host interpreter clean (ClassEval
    solutions freely import random libraries).
    """
    return textwrap.dedent(r'''
        import io, json, sys, traceback, unittest, importlib.util, importlib, os, re

        payload = json.loads(sys.stdin.read())
        solution_path = payload["solution_path"]
        imports = payload["imports"]
        test_classes = payload["test_classes"]  # list[str]
        class_name = payload["class_name"]

        # Load the generated class into a throwaway module.
        spec = importlib.util.spec_from_file_location("_sol", solution_path)
        mod = importlib.util.module_from_spec(spec)
        ns = mod.__dict__

        # Pre-execute the required imports in the module namespace so the
        # generated class sees them even if the model omitted them.
        try:
            exec(compile(imports, "<imports>", "exec"), ns)
        except Exception as e:
            print(json.dumps({
                "ok": False, "class_load_error": f"imports failed: {e}",
                "methods": {},
            }))
            sys.exit(0)

        try:
            spec.loader.exec_module(mod)
        except Exception:
            print(json.dumps({
                "ok": False,
                "class_load_error": "solution exec failed: " + traceback.format_exc()[-1500:],
                "methods": {},
            }))
            sys.exit(0)

        # Expose the generated class into the loader namespace if needed.
        if class_name not in ns and class_name in mod.__dict__:
            ns[class_name] = mod.__dict__[class_name]

        # Also import the solution via `solution.py` path so tests that
        # do `from solution import X` can find it.
        sys.path.insert(0, os.path.dirname(solution_path))
        if "solution" in sys.modules:
            del sys.modules["solution"]
        try:
            sol_mod = importlib.import_module("solution")
        except Exception:
            sol_mod = None

        method_results = {}
        any_err = False
        for test_src in test_classes:
            test_ns = dict(ns)
            test_ns["unittest"] = unittest
            # Expose the class to the test namespace under its real name.
            if sol_mod is not None and class_name in sol_mod.__dict__:
                test_ns[class_name] = sol_mod.__dict__[class_name]
            elif class_name in mod.__dict__:
                test_ns[class_name] = mod.__dict__[class_name]

            m = re.search(r"class\s+(\w+)\s*\(", test_src)
            tclass_name = m.group(1) if m else "UnknownTest"

            try:
                exec(compile(test_src, f"<{tclass_name}>", "exec"), test_ns)
            except Exception:
                method_results[tclass_name] = {
                    "passed": False,
                    "error": "test exec failed: " + traceback.format_exc()[-500:],
                    "tests_run": 0, "failures": 0, "errors": 1,
                }
                any_err = True
                continue

            TestCls = test_ns.get(tclass_name)
            if TestCls is None:
                method_results[tclass_name] = {
                    "passed": False, "error": "test class not found",
                    "tests_run": 0, "failures": 0, "errors": 1,
                }
                any_err = True
                continue

            loader = unittest.TestLoader()
            suite = loader.loadTestsFromTestCase(TestCls)
            buf = io.StringIO()
            runner = unittest.TextTestRunner(stream=buf, verbosity=0)
            result = runner.run(suite)
            passed = result.wasSuccessful()
            method_results[tclass_name] = {
                "passed": passed,
                "error": "" if passed else buf.getvalue()[-800:],
                "tests_run": result.testsRun,
                "failures": len(result.failures),
                "errors": len(result.errors),
            }
            if not passed:
                any_err = True

        print(json.dumps({
            "ok": not any_err,
            "class_load_error": "",
            "methods": method_results,
        }))
    ''').strip()


def evaluate(task: dict, solution_path: Path, timeout: int = 60) -> dict:
    """Return dict: {ok, class_passed, method_pass_count, method_total,
                    method_results, class_load_error}."""
    script = _evaluator_script()
    with tempfile.NamedTemporaryFile(
        "w", suffix="_ceval.py", delete=False, encoding="utf-8"
    ) as tf:
        tf.write(script)
        script_path = tf.name

    # ClassEval's `test_classes` is a list of NAMES only; the real source is
    # inside methods_info[i].test_code. Assemble the source list here.
    test_sources = [mi["test_code"] for mi in task.get("methods_info", [])
                    if mi.get("test_code")]
    payload = {
        "solution_path": str(solution_path),
        "imports": task.get("import_statement", ""),
        "class_name": task["class_name"],
        "test_classes": test_sources,
    }

    try:
        r = subprocess.run(
            [sys.executable, script_path],
            input=json.dumps(payload),
            capture_output=True, encoding="utf-8", errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {
            "ok": False, "class_passed": False,
            "method_pass_count": 0, "method_total": len(test_sources),
            "method_results": {}, "class_load_error": f"evaluator timeout ({timeout}s)",
        }
    finally:
        try:
            Path(script_path).unlink()
        except OSError:
            pass

    stdout = (r.stdout or "").strip()
    stderr = (r.stderr or "").strip()
    if r.returncode != 0 or not stdout:
        return {
            "ok": False, "class_passed": False,
            "method_pass_count": 0, "method_total": len(test_sources),
            "method_results": {},
            "class_load_error": f"evaluator subprocess failed: rc={r.returncode}, {(stderr or stdout)[:500]}",
        }

    # Take the last parseable JSON line (the script may have earlier noise).
    last_json = None
    for line in stdout.splitlines()[::-1]:
        line = line.strip()
        if line.startswith("{"):
            try:
                last_json = json.loads(line)
                break
            except json.JSONDecodeError:
                continue
    if last_json is None:
        return {
            "ok": False, "class_passed": False,
            "method_pass_count": 0, "method_total": len(test_sources),
            "method_results": {},
            "class_load_error": f"evaluator stdout unparseable: {stdout[:500]}",
        }

    methods = last_json.get("methods", {})
    method_pass = sum(1 for m in methods.values() if m.get("passed"))
    method_total = len(methods) or len(test_sources)
    class_passed = last_json.get("ok", False) and method_pass == method_total and method_total > 0
    return {
        "ok": last_json.get("ok", False),
        "class_passed": class_passed,
        "method_pass_count": method_pass,
        "method_total": method_total,
        "method_results": methods,
        "class_load_error": last_json.get("class_load_error", ""),
    }
