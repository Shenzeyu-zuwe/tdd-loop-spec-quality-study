"""ClassEval benchmark harness for the TDD-Loop framework.

Compares two configurations on the FudanSELab ClassEval (100-class Python
benchmark):

  1. **baseline**: single-shot `claude -p` generates the entire class given
     skeleton + docstrings.
  2. **tdd_loop**: the class is decomposed into a feature_list.json (one
     feature per method), run through the tdd_loop orchestrator.

Both configurations produce a generated class file, which is then evaluated
against ClassEval's original unittest test suite. The score metric is
ClassEval's official class-level pass@1 (a task passes iff every per-method
test class passes).
"""
