# -*- coding: utf-8 -*-
"""Python-local environment.

Tells the Tester/Worker the project is a Python module at `solution.py` in
the project root, and that runtime verification must use the Bash tool to
execute Python code.

No harness process is spawned — the Bash tool (which every Claude CLI
session has) is sufficient for `python -c`, temp scripts, and pytest.
"""

from tdd_loop.environment import Environment


class PythonLocalEnvironment(Environment):
    name = "python_local"
    capabilities = (
        "This is a Python project rooted at the current working directory. "
        "The solution file is `solution.py` at the project root and defines "
        "the class specified in the spec.\n"
        "\n"
        "Runtime verification protocol (use this for every test intent):\n"
        "  1. Write a self-contained Python script to a temp file in the "
        "project root, e.g. `_probe.py`.\n"
        "  2. The script must `from solution import <ClassName>` to load "
        "the generated code from the file actually on disk (NOT from your "
        "reading of the source).\n"
        "  3. Execute via Bash: `python _probe.py` and capture stdout/stderr.\n"
        "  4. Compare actual stdout to the expected output the intent "
        "specifies, byte-by-byte after stripping trailing whitespace.\n"
        "  5. Clean up the temp file after the check.\n"
        "\n"
        "Important:\n"
        "  - If you did not run `python` and observe stdout, you did not "
        "verify. Code review alone → `failure_type: test_env_error`.\n"
        "  - If the script raises → `failure_type: bug` with the traceback "
        "in details.\n"
        "  - If stdout diverges from expected → `failure_type: bug` with a "
        "diff in details.\n"
        "  - Runtime evidence always overrides what the source \"looks like\"."
    )

    # Tokens that should appear in runtime-check intents for them to count
    # as anchored by the intent-linter.
    anchor_patterns = [
        r"\bpython\b", r"\bstdout\b", r"\bexpected\s+output\b",
        r"`python\s", r"python _?\w+\.py",
    ]


def build(**kwargs):
    return PythonLocalEnvironment()
