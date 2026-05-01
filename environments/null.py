# -*- coding: utf-8 -*-
"""Null environment — no runtime harness, code-review verification only."""

from tdd_loop.environment import NullEnvironment


def build(**kwargs):
    return NullEnvironment()
