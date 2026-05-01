# -*- coding: utf-8 -*-
"""
Agent handoff — session-interruption continuation.

Design principle: pass only *disk facts* (file paths, git diff) to a resumed
session, never the previous agent's self-reported output. Self-reports can be
wrong or truncated; disk is authoritative.
"""

import subprocess
from pathlib import Path


def git_diff_name_only(project_dir: Path) -> str:
    try:
        r = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            cwd=str(project_dir), capture_output=True,
            encoding="utf-8", errors="replace", timeout=10,
        )
        return r.stdout.strip()
    except Exception:
        return "(git diff failed)"


def build_handoff(role: str, exit_reason: str, project_dir: Path) -> str:
    if role == "worker":
        modified = git_diff_name_only(project_dir)
        return (
            f"Previous session was interrupted: [{exit_reason}].\n"
            f"The following files may be partially modified; read them first to "
            f"confirm their current state before continuing:\n{modified}"
        )
    return f"Previous session was interrupted: [{exit_reason}]. Please restart the task."
