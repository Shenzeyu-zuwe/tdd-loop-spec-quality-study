# TDDLoop Report

| | |
|---|---|
| Result | **ALL PASSED** |
| Change | ClassEval_15 |
| Environment | python_local |
| Start | 2026-04-27 10:45:14 |
| End | 2026-04-27 10:52:05 |
| Duration | 6m51s |
| Iterations | 3 |
| Model | haiku |
| Cost | $0.6593 |
| Sessions | 21 |

## Features (3/3 passed)

### [PASSED] F-001 Method `match_in_pattern(self, char)` on class `BoyerMooreSearch` passes its hidden unit-test suite (oracle ablation arm).

- [✓] **T-001-01** ORACLE TEST RUN for `BoyerMooreSearch.match_in_pattern`.

Write the following Python code to a temp file (e.g. `_oracle_match_in_pattern.py`) in the project root and execute `python _oracle_match_in_pattern.py` via the Bash tool. The script runs the hidden unit tests for this method.

PASS criteria: process exits with code 0 AND unittest reports `OK` (no failures, no errors).
FAIL criteria: any failure, error, exception, or non-zero exit. Do NOT modify the test code. Do NOT infer the result without actually executing the script.

Script:
```python
import sys, unittest
sys.path.insert(0, '.')

from solution import BoyerMooreSearch

class BoyerMooreSearchTestMatchInPattern(unittest.TestCase):
    def test_match_in_pattern(self):
        boyerMooreSearch = BoyerMooreSearch("ABAABA", "AB")
        self.assertEqual(boyerMooreSearch.match_in_pattern("A"), 0)

    def test_match_in_pattern_2(self):
        boyerMooreSearch = BoyerMooreSearch("ABAABA", "ABAB")
        self.assertEqual(boyerMooreSearch.match_in_pattern("B"), 3)

    def test_match_in_pattern_3(self):
        boyerMooreSearch = BoyerMooreSearch("ABAABA", "ABCABC")
        self.assertEqual(boyerMooreSearch.match_in_pattern("C"), 5)

    def test_match_in_pattern_4(self):
        boyerMooreSearch = BoyerMooreSearch("ABAABA", "ABCABC")
        self.assertEqual(boyerMooreSearch.match_in_pattern("D"), -1)

    def test_match_in_pattern_5(self):
        boyerMooreSearch = BoyerMooreSearch("ABAABA", "ABCABC")
        self.assertEqual(boyerMooreSearch.match_in_pattern("E"), -1)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(BoyerMooreSearchTestMatchInPattern)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
```

  - All 5 test cases passed. The match_in_pattern method correctly returns the rightmost occurrence index of a character in the pattern using rfind, or -1 if not found.

### [PASSED] F-002 Method `mismatch_in_text(self, currentPos)` on class `BoyerMooreSearch` passes its hidden unit-test suite (oracle ablation arm).

- [✓] **T-002-01** ORACLE TEST RUN for `BoyerMooreSearch.mismatch_in_text`.

Write the following Python code to a temp file (e.g. `_oracle_mismatch_in_text.py`) in the project root and execute `python _oracle_mismatch_in_text.py` via the Bash tool. The script runs the hidden unit tests for this method.

PASS criteria: process exits with code 0 AND unittest reports `OK` (no failures, no errors).
FAIL criteria: any failure, error, exception, or non-zero exit. Do NOT modify the test code. Do NOT infer the result without actually executing the script.

Script:
```python
import sys, unittest
sys.path.insert(0, '.')

from solution import BoyerMooreSearch

class BoyerMooreSearchTestMismatchInText(unittest.TestCase):
    def test_mismatch_in_text(self):
        boyerMooreSearch = BoyerMooreSearch("ABAABA", "AB")
        self.assertEqual(boyerMooreSearch.mismatch_in_text(0), -1)

    def test_mismatch_in_text_2(self):
        boyerMooreSearch = BoyerMooreSearch("ABAABA", "ABC")
        self.assertEqual(boyerMooreSearch.mismatch_in_text(0), 2)

    def test_mismatch_in_text_3(self):
        boyerMooreSearch = BoyerMooreSearch("AAAA", "ABC")
        self.assertEqual(boyerMooreSearch.mismatch_in_text(0), 2)

    def test_mismatch_in_text_4(self):
        boyerMooreSearch = BoyerMooreSearch("ABAABA", "")
        self.assertEqual(boyerMooreSearch.mismatch_in_text(0), -1)

    def test_mismatch_in_text_5(self):
        boyerMooreSearch = BoyerMooreSearch("ABAABA", "ABC")
        self.assertEqual(boyerMooreSearch.mismatch_in_text(3), 5)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(BoyerMooreSearchTestMismatchInText)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
```

  - All 5 unit tests passed. Test execution completed with exit code 0 and unittest reported OK with no failures or errors.

### [PASSED] F-003 Method `bad_character_heuristic(self)` on class `BoyerMooreSearch` passes its hidden unit-test suite (oracle ablation arm).

- [✓] **T-003-01** ORACLE TEST RUN for `BoyerMooreSearch.bad_character_heuristic`.

Write the following Python code to a temp file (e.g. `_oracle_bad_character_heuristic.py`) in the project root and execute `python _oracle_bad_character_heuristic.py` via the Bash tool. The script runs the hidden unit tests for this method.

PASS criteria: process exits with code 0 AND unittest reports `OK` (no failures, no errors).
FAIL criteria: any failure, error, exception, or non-zero exit. Do NOT modify the test code. Do NOT infer the result without actually executing the script.

Script:
```python
import sys, unittest
sys.path.insert(0, '.')

from solution import BoyerMooreSearch

class BoyerMooreSearchTestBadCharacterHeuristic(unittest.TestCase):
    def test_bad_character_heuristic(self):
        boyerMooreSearch = BoyerMooreSearch("ABAABA", "AB")
        self.assertEqual(boyerMooreSearch.bad_character_heuristic(), [0, 3])

    def test_bad_character_heuristic_2(self):
        boyerMooreSearch = BoyerMooreSearch("ABAABA", "ABC")
        self.assertEqual(boyerMooreSearch.bad_character_heuristic(), [])

    def test_bad_character_heuristic_3(self):
        boyerMooreSearch = BoyerMooreSearch("ABAABA", "")
        self.assertEqual(boyerMooreSearch.bad_character_heuristic(), [0, 1, 2, 3, 4, 5, 6])

    def test_bad_character_heuristic_4(self):
        boyerMooreSearch = BoyerMooreSearch("ABACABA", "ABA")
        self.assertEqual(boyerMooreSearch.bad_character_heuristic(), [0, 4])

    def test_bad_character_heuristic_5(self):
        boyerMooreSearch = BoyerMooreSearch("ABACABA", "ABAC")
        self.assertEqual(boyerMooreSearch.bad_character_heuristic(), [0])

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(BoyerMooreSearchTestBadCharacterHeuristic)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
```

  - Oracle test script executed successfully with exit code 0. All 5 test cases passed: basic pattern matching, pattern not found, empty pattern edge case, multiple occurrences, and partial matches.

## Sessions (21 total, $0.6593)

| # | Role | Feature | Task | Status | Duration | Cost | Session ID |
|---|------|---------|------|--------|----------|------|------------|
| 1 | Tester | F-001 | verify T-001-01 | error | 1s | $0.0000 | 80c3b945-866.. |
| 2 | Worker | F-001 | fix 1 tests | error | 1s | $0.0000 | 60ba6173-d2c.. |
| 3 | Tester | F-001 | verify T-001-01 | error | 1s | $0.0000 | 82e16cfc-8bf.. |
| 4 | Tester | F-002 | verify T-002-01 | error | 1s | $0.0000 | 717c5d2d-81b.. |
| 5 | Worker | F-002 | fix 1 tests | error | 1s | $0.0000 | 3ae5ddcc-4b0.. |
| 6 | Tester | F-002 | verify T-002-01 | error | 1s | $0.0000 | a02e540a-d5c.. |
| 7 | Tester | F-003 | verify T-003-01 | error | 1s | $0.0000 | 2e88d2e6-6d9.. |
| 8 | Worker | F-003 | fix 1 tests | error | 1s | $0.0000 | 9d8f3c69-9df.. |
| 9 | Tester | F-003 | verify T-003-01 | error | 1s | $0.0000 | 0c9dfa7e-872.. |
| 10 | Tester | F-001 | verify T-001-01 | ok | 23s | $0.0454 | b60e4fd8-f0e.. |
| 11 | Worker | F-001 | fix 1 tests | ok | 24s | $0.0507 | ff298ebc-f2e.. |
| 12 | Tester | F-001 | verify T-001-01 | ok | 26s | $0.0492 | ac766af7-167.. |
| 13 | Tester | F-002 | verify T-002-01 | ok | 33s | $0.0505 | efda460a-44f.. |
| 14 | Worker | F-002 | fix 1 tests | ok | 45s | $0.0696 | 7765ab3d-a82.. |
| 15 | Tester | F-002 | verify T-002-01 | ok | 29s | $0.0522 | e1c3e5c6-bf0.. |
| 16 | Tester | F-003 | verify T-003-01 | ok | 25s | $0.0449 | 0e1f4c09-038.. |
| 17 | Worker | F-003 | fix 1 tests | ok | 1m3s | $0.0980 | 176e2fbb-973.. |
| 18 | Tester | F-003 | verify T-003-01 | ok | 31s | $0.0568 | 3b507ec4-bd0.. |
| 19 | Tester | F-001 | verify T-001-01 | ok | 34s | $0.0557 | 7c724f0c-059.. |
| 20 | Tester | F-002 | verify T-002-01 | ok | 20s | $0.0423 | 9a962d39-761.. |
| 21 | Tester | F-003 | verify T-003-01 | ok | 22s | $0.0439 | 4dca44a6-974.. |