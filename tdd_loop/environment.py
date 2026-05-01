# -*- coding: utf-8 -*-
"""
Environment — pluggable runtime harness for the TDD loop.

An Environment is the thing that the Tester agent can poke at to verify an
intent has been realised at runtime. Examples:

  * NullEnvironment      — no runtime; Tester verifies via code reading only
                            (good for pure-library tasks and code-level specs)
  * ProcessEnvironment   — spawn/kill a server or CLI subprocess per task
  * NetworkEnvironment   — live HTTP endpoint (the Tester issues requests)
  * GameClientEnvironment (project-specific) — telnet into a running game
                            client, hot-reload modules, screenshot UI

The orchestrator's core loop knows nothing about the environment beyond the
lifecycle methods defined below. The Tester prompt is templated with the
environment's capabilities description so it knows what probes are available.

Separating the environment out is what lets this framework be the same code
across benchmark domains — which is also what makes it interesting as a
research artifact rather than a one-off tool.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("tdd_loop.env")


class Environment:
    """Base class. Override what your harness needs."""

    # Name used in logs and the Tester prompt.
    name: str = "null"

    # Natural-language description injected into the Tester system prompt
    # under a "## Verification Harness" section. Tell the Tester what it can
    # and cannot do. Keep it concrete: list the exact commands/APIs.
    capabilities: str = (
        "No runtime harness is attached. Verify intents by reading code "
        "(Grep/Glob/Read) and reasoning about correctness at the source level."
    )

    # Extra anchor regex patterns added to the intent linter for this env.
    anchor_patterns: list[str] = []

    # Environment variables to inject into Tester/Worker subprocesses.
    # Keys + string values; use this to hand the Tester a session token,
    # endpoint URL, tempdir path, etc. without hard-coding in prompts.
    def env_vars(self) -> dict[str, str]:
        return {}

    # ── Lifecycle hooks ──────────────────────────────────────────

    def ensure(self) -> bool:
        """Bring the environment up. Called once, after orchestrator init,
        before the main loop starts.

        Return True iff the environment is ready for verification.
        A False return does not abort the loop — the Tester will be told
        the harness is unavailable and should report `test_env_error`
        instead of fabricating passes.
        """
        return True

    def health_check(self) -> bool:
        """Cheap readiness probe. Called before each Tester invocation.
        Should self-heal (e.g. restart) if possible. Return current state."""
        return True

    def shutdown(self) -> None:
        """Tear down resources owned by this environment. Called on every
        exit path (success, failure, Ctrl-C). Must be idempotent."""
        return None

    # ── Optional verification-side helpers ───────────────────────
    #
    # These are surfaced to the Tester via the prompt. Default impls are
    # no-ops so a NullEnvironment still satisfies the interface.

    def notify_pre_verify(self, feature_id: str, test_id: str) -> None:
        """Hook before a single Tester invocation. Use e.g. to reset state,
        snapshot logs, or clear caches between tests."""
        return None

    def notify_post_worker(self, modified_files: list[str]) -> None:
        """Hook after a Worker invocation, passed the list of files the
        Worker touched (from git diff). Use e.g. to hot-reload modules."""
        return None

    # ── Metadata for status dumps ────────────────────────────────

    def describe(self) -> dict[str, Any]:
        return {"name": self.name, "capabilities_preview": self.capabilities[:120]}


class NullEnvironment(Environment):
    """No runtime harness. Tester verifies by reading code only.

    Appropriate for: pure library code; schema / API shape checks; anything
    where correctness is statically decidable. This is the default.
    """
    name = "null"
