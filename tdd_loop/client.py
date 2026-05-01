# -*- coding: utf-8 -*-
"""
LLM client factory — Claude Code CLI backend.

The framework only depends on the subprocess interface, so swapping in other
CLI-style agents (Aider, OpenCode, codex) is a matter of replacing agent.py.
"""

DEFAULT_MODEL = "sonnet"


def create_client(model: str | None = None):
    """Return (client, model_name, backend_name).

    client is None because subprocess-based CLIs don't need a persistent object.
    Kept as a tuple for forward-compatibility with SDK-based backends.
    """
    return None, (model or DEFAULT_MODEL), "claude_code_cli"
