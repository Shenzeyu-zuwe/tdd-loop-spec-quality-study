"""Pluggable Environment implementations.

Each module here exposes a `build(**kwargs) -> Environment` factory so the
orchestrator can load environments by string name from the CLI.
"""
