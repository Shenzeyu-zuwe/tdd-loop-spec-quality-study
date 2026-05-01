# -*- coding: utf-8 -*-
"""SWE-bench repo environment plugin — thin shim over experiments/swebench_lite/env_repo.

Loaded via `--environment swebench_repo --env-arg repo=...` from the SWE-bench
runner. Keeps the heavy lifting in the experiments package (where it belongs)
while exposing the standard `build(**kwargs)` entry point the orchestrator
expects in environments/.
"""
from experiments.swebench_lite.env_repo import build  # noqa: F401
