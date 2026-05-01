# -*- coding: utf-8 -*-
"""Repository Environment for SWE-bench Lite tasks.

Per task:
  1. clone (or reuse cache of) the target repo at base_commit
  2. install editable in a fresh venv (or reuse cached venv)
  3. expose pytest as the runtime probe via env_vars + capabilities

The Tester / baseline reads `PROBLEM.md` for the issue text and uses the
shell to run pytest on FAIL_TO_PASS tests via the documented command in
`capabilities`.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from tdd_loop.environment import Environment

CACHE_ROOT = Path(__file__).resolve().parent / "_repo_cache"


class SWEBenchRepoEnvironment(Environment):
    name = "swebench_repo"
    capabilities = (
        "Repository under test is checked out at $TDD_REPO_DIR. "
        "Run tests with: `cd $TDD_REPO_DIR && python -m pytest -xvs <test_node_id>`. "
        "Editable install is already done; do not re-install. "
        "Apply edits directly to source files in $TDD_REPO_DIR."
    )

    def __init__(self, repo: str, base_commit: str, instance_id: str):
        self.repo = repo  # e.g. "pallets/flask"
        self.base_commit = base_commit
        self.instance_id = instance_id
        self.repo_dir: Path = CACHE_ROOT / instance_id

    # --- lifecycle ---

    def ensure(self) -> bool:
        CACHE_ROOT.mkdir(parents=True, exist_ok=True)
        if not (self.repo_dir / ".git").exists():
            self._clone()
        self._reset_to_base()
        self._install()
        return True

    def health_check(self) -> bool:
        try:
            cp = subprocess.run(
                [sys.executable, "-m", "pytest", "--collect-only", "-q"],
                cwd=self.repo_dir, capture_output=True, text=True, timeout=120,
            )
            return cp.returncode in (0, 5)  # 5 = no tests collected, still alive
        except Exception:
            return False

    def shutdown(self) -> None:
        # Keep the cache; SWE-bench Lite repos are small and cache speeds reruns.
        pass

    # --- hooks for orchestrator ---

    def env_vars(self) -> dict[str, str]:
        return {"TDD_REPO_DIR": str(self.repo_dir)}

    def notify_pre_verify(self, *args, **kwargs) -> None:
        pass

    def notify_post_worker(self, *args, **kwargs) -> None:
        pass

    # --- internals ---

    def _clone(self) -> None:
        url = f"https://github.com/{self.repo}.git"
        subprocess.check_call(["git", "clone", "--depth", "1", url, str(self.repo_dir)])

    def _reset_to_base(self) -> None:
        # ensure we have the base_commit fetched
        subprocess.run(["git", "fetch", "--depth", "1", "origin", self.base_commit],
                       cwd=self.repo_dir, check=False)
        subprocess.check_call(["git", "checkout", "-f", self.base_commit], cwd=self.repo_dir)
        subprocess.run(["git", "clean", "-fdx"], cwd=self.repo_dir, check=False)

    def _install(self) -> None:
        # Lightweight editable install. Real SWE-bench harness uses pinned
        # python versions and full requirements; this is the docker-less path.
        for cmd in (
            [sys.executable, "-m", "pip", "install", "-q", "-e", "."],
            [sys.executable, "-m", "pip", "install", "-q", "pytest"],
        ):
            subprocess.run(cmd, cwd=self.repo_dir, check=False, capture_output=True)


def build(**kwargs) -> SWEBenchRepoEnvironment:
    return SWEBenchRepoEnvironment(
        repo=kwargs["repo"],
        base_commit=kwargs["base_commit"],
        instance_id=kwargs["instance_id"],
    )
