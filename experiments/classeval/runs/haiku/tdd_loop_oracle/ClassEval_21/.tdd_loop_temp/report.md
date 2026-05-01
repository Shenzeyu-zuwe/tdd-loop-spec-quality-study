# TDDLoop Report

| | |
|---|---|
| Result | **ALL PASSED** |
| Change | ClassEval_21 |
| Environment | python_local |
| Start | 2026-04-27 11:50:17 |
| End | 2026-04-27 11:59:15 |
| Duration | 8m58s |
| Iterations | 4 |
| Model | haiku |
| Cost | $0.8424 |
| Sessions | 28 |

## Features (4/4 passed)

### [PASSED] F-001 Method `add_course(self, course)` on class `Classroom` passes its hidden unit-test suite (oracle ablation arm).

- [✓] **T-001-01** ORACLE TEST RUN for `Classroom.add_course`.

Write the following Python code to a temp file (e.g. `_oracle_add_course.py`) in the project root and execute `python _oracle_add_course.py` via the Bash tool. The script runs the hidden unit tests for this method.

PASS criteria: process exits with code 0 AND unittest reports `OK` (no failures, no errors).
FAIL criteria: any failure, error, exception, or non-zero exit. Do NOT modify the test code. Do NOT infer the result without actually executing the script.

Script:
```python
import sys, unittest
sys.path.insert(0, '.')
from datetime import datetime
from solution import Classroom

class ClassroomTestAddCourse(unittest.TestCase):
    def test_add_course_1(self):
        classroom = Classroom(1)
        course = {'name': 'math', 'start_time': '09:00', 'end_time': '10:00'}
        classroom.add_course(course)
        self.assertIn(course, classroom.courses)

    def test_add_course_2(self):
        classroom = Classroom(1)
        course = {'name': 'Chinese', 'start_time': '10:00', 'end_time': '11:00'}
        classroom.add_course(course)
        self.assertIn(course, classroom.courses)

    def test_add_course_3(self):
        classroom = Classroom(1)
        course = {'name': 'English', 'start_time': '11:00', 'end_time': '12:00'}
        classroom.add_course(course)
        self.assertIn(course, classroom.courses)

    def test_add_course_4(self):
        classroom = Classroom(1)
        course = {'name': 'Art', 'start_time': '14:00', 'end_time': '15:00'}
        classroom.add_course(course)
        self.assertIn(course, classroom.courses)

    def test_add_course_5(self):
        classroom = Classroom(1)
        course = {'name': 'P.E.', 'start_time': '15:00', 'end_time': '16:00'}
        classroom.add_course(course)
        self.assertIn(course, classroom.courses)

    def test_add_course_6(self):
        classroom = Classroom(1)
        course = {'name': 'math', 'start_time': '09:00', 'end_time': '10:00'}
        classroom.add_course(course)
        classroom.add_course(course)
        self.assertIn(course, classroom.courses)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(ClassroomTestAddCourse)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
```

  - All 6 oracle unit tests passed with exit code 0 and OK status. The add_course method correctly adds courses to the list while preventing duplicates.

### [PASSED] F-002 Method `remove_course(self, course)` on class `Classroom` passes its hidden unit-test suite (oracle ablation arm).

- [✓] **T-002-01** ORACLE TEST RUN for `Classroom.remove_course`.

Write the following Python code to a temp file (e.g. `_oracle_remove_course.py`) in the project root and execute `python _oracle_remove_course.py` via the Bash tool. The script runs the hidden unit tests for this method.

PASS criteria: process exits with code 0 AND unittest reports `OK` (no failures, no errors).
FAIL criteria: any failure, error, exception, or non-zero exit. Do NOT modify the test code. Do NOT infer the result without actually executing the script.

Script:
```python
import sys, unittest
sys.path.insert(0, '.')
from datetime import datetime
from solution import Classroom

class ClassroomTestRemoveCourse(unittest.TestCase):
    def test_remove_course_1(self):
        classroom = Classroom(1)
        course = {'name': 'math', 'start_time': '09:00', 'end_time': '10:00'}
        classroom.add_course(course)
        classroom.remove_course(course)
        self.assertNotIn(course, classroom.courses)

    def test_remove_course_2(self):
        classroom = Classroom(1)
        course = {'name': 'Chinese', 'start_time': '10:00', 'end_time': '11:00'}
        classroom.add_course(course)
        classroom.remove_course(course)
        self.assertNotIn(course, classroom.courses)

    def test_remove_course_3(self):
        classroom = Classroom(1)
        course = {'name': 'English', 'start_time': '11:00', 'end_time': '12:00'}
        classroom.add_course(course)
        classroom.remove_course(course)
        self.assertNotIn(course, classroom.courses)

    def test_remove_course_4(self):
        classroom = Classroom(1)
        course = {'name': 'Art', 'start_time': '14:00', 'end_time': '15:00'}
        classroom.add_course(course)
        classroom.remove_course(course)
        self.assertNotIn(course, classroom.courses)

    def test_remove_course_5(self):
        classroom = Classroom(1)
        course = {'name': 'P.E.', 'start_time': '15:00', 'end_time': '16:00'}
        classroom.add_course(course)
        classroom.remove_course(course)
        self.assertNotIn(course, classroom.courses)

    def test_remove_course_6(self):
        classroom = Classroom(1)
        course = {'name': 'math', 'start_time': '09:00', 'end_time': '10:00'}
        classroom.remove_course(course)
        self.assertNotIn(course, classroom.courses)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(ClassroomTestRemoveCourse)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
```

  - All 6 oracle unit tests for remove_course executed successfully with exit code 0 and reported OK (no failures, no errors).

### [PASSED] F-003 Method `is_free_at(self, check_time)` on class `Classroom` passes its hidden unit-test suite (oracle ablation arm).

- [✓] **T-003-01** ORACLE TEST RUN for `Classroom.is_free_at`.

Write the following Python code to a temp file (e.g. `_oracle_is_free_at.py`) in the project root and execute `python _oracle_is_free_at.py` via the Bash tool. The script runs the hidden unit tests for this method.

PASS criteria: process exits with code 0 AND unittest reports `OK` (no failures, no errors).
FAIL criteria: any failure, error, exception, or non-zero exit. Do NOT modify the test code. Do NOT infer the result without actually executing the script.

Script:
```python
import sys, unittest
sys.path.insert(0, '.')
from datetime import datetime
from solution import Classroom

class ClassroomTestIsFreeAt(unittest.TestCase):
    def test_is_free_at_1(self):
        classroom = Classroom(1)
        course = {'name': 'math', 'start_time': '09:00', 'end_time': '10:00'}
        classroom.add_course(course)
        check_time = '11:00'
        result = classroom.is_free_at(check_time)
        self.assertTrue(result)

    def test_is_free_at_2(self):
        classroom = Classroom(1)
        course = {'name': 'math', 'start_time': '09:00', 'end_time': '10:00'}
        classroom.add_course(course)
        check_time = '09:30'
        result = classroom.is_free_at(check_time)
        self.assertFalse(result)

    def test_is_free_at_3(self):
        classroom = Classroom(1)
        course = {'name': 'math', 'start_time': '09:00', 'end_time': '10:00'}
        classroom.add_course(course)
        check_time = '12:00'
        result = classroom.is_free_at(check_time)
        self.assertTrue(result)

    def test_is_free_at_4(self):
        classroom = Classroom(1)
        course = {'name': 'math', 'start_time': '09:00', 'end_time': '10:00'}
        classroom.add_course(course)
        check_time = '14:00'
        result = classroom.is_free_at(check_time)
        self.assertTrue(result)

    def test_is_free_at_5(self):
        classroom = Classroom(1)
        course = {'name': 'math', 'start_time': '09:00', 'end_time': '10:00'}
        classroom.add_course(course)
        check_time = '09:40'
        result = classroom.is_free_at(check_time)
        self.assertFalse(result)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(ClassroomTestIsFreeAt)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
```

  - All 5 oracle unit tests for is_free_at passed. Process exited with code 0 and unittest reported OK with no failures or errors.

### [PASSED] F-004 Method `check_course_conflict(self, new_course)` on class `Classroom` passes its hidden unit-test suite (oracle ablation arm).

- [✓] **T-004-01** ORACLE TEST RUN for `Classroom.check_course_conflict`.

Write the following Python code to a temp file (e.g. `_oracle_check_course_conflict.py`) in the project root and execute `python _oracle_check_course_conflict.py` via the Bash tool. The script runs the hidden unit tests for this method.

PASS criteria: process exits with code 0 AND unittest reports `OK` (no failures, no errors).
FAIL criteria: any failure, error, exception, or non-zero exit. Do NOT modify the test code. Do NOT infer the result without actually executing the script.

Script:
```python
import sys, unittest
sys.path.insert(0, '.')
from datetime import datetime
from solution import Classroom

class ClassroomTestCheckCourseConflict(unittest.TestCase):
    def test_check_course_conflict_1(self):
        classroom = Classroom(1)
        existing_course = {'name': 'math', 'start_time': '09:00', 'end_time': '10:00'}
        classroom.add_course(existing_course)
        new_course = {'name': 'SE', 'start_time': '10:30', 'end_time': '11:30'}
        result = classroom.check_course_conflict(new_course)
        self.assertTrue(result)

    def test_check_course_conflict_2(self):
        classroom = Classroom(1)
        existing_course = {'name': 'math', 'start_time': '09:00', 'end_time': '10:00'}
        classroom.add_course(existing_course)
        new_course = {'name': 'SE', 'start_time': '09:30', 'end_time': '10:30'}
        result = classroom.check_course_conflict(new_course)
        self.assertFalse(result)

    # have the same boundary time
    # existing_course['end_time'] == new_course['start_time']
    def test_check_course_conflict_3(self):
        classroom = Classroom(1)
        existing_course = {'name': 'math', 'start_time': '09:00', 'end_time': '10:00'}
        classroom.add_course(existing_course)
        new_course = {'name': 'SE', 'start_time': '10:00', 'end_time': '11:30'}
        result = classroom.check_course_conflict(new_course)
        self.assertFalse(result)

    def test_check_course_conflict_4(self):
        classroom = Classroom(1)
        existing_course = {'name': 'math', 'start_time': '09:00', 'end_time': '10:00'}
        classroom.add_course(existing_course)
        new_course = {'name': 'SE', 'start_time': '09:40', 'end_time': '10:40'}
        result = classroom.check_course_conflict(new_course)
        self.assertFalse(result)

    def test_check_course_conflict_5(self):
        classroom = Classroom(1)
        existing_course = {'name': 'math', 'start_time': '09:00', 'end_time': '10:00'}
        classroom.add_course(existing_course)
        new_course = {'name': 'SE', 'start_time': '14:30', 'end_time': '15:30'}
        result = classroom.check_course_conflict(new_course)
        self.assertTrue(result)

    def test_check_course_conflict_6(self):
        classroom = Classroom(1)
        existing_course = {'name': 'math', 'start_time': '09:00', 'end_time': '10:00'}
        classroom.add_course(existing_course)
        new_course = {'name': 'SE', 'start_time': '8:30', 'end_time': '9:30'}
        result = classroom.check_course_conflict(new_course)
        self.assertFalse(result)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(ClassroomTestCheckCourseConflict)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
```

  - All 6 oracle unit tests passed. Test execution completed successfully with exit code 0 and unittest reported OK (no failures, no errors).

## Sessions (28 total, $0.8424)

| # | Role | Feature | Task | Status | Duration | Cost | Session ID |
|---|------|---------|------|--------|----------|------|------------|
| 1 | Tester | F-001 | verify T-001-01 | error | 1s | $0.0000 | d79ab040-ebc.. |
| 2 | Worker | F-001 | fix 1 tests | error | 1s | $0.0000 | 68f90360-b71.. |
| 3 | Tester | F-001 | verify T-001-01 | error | 1s | $0.0000 | cd564648-6b8.. |
| 4 | Tester | F-002 | verify T-002-01 | error | 1s | $0.0000 | b55bba6d-53e.. |
| 5 | Worker | F-002 | fix 1 tests | error | 1s | $0.0000 | 60f13e81-2a3.. |
| 6 | Tester | F-002 | verify T-002-01 | error | 1s | $0.0000 | 629fcaf4-43e.. |
| 7 | Tester | F-003 | verify T-003-01 | error | 1s | $0.0000 | db7625c1-733.. |
| 8 | Worker | F-003 | fix 1 tests | error | 1s | $0.0000 | a143f763-ada.. |
| 9 | Tester | F-003 | verify T-003-01 | error | 1s | $0.0000 | 8f0e384e-3cc.. |
| 10 | Tester | F-004 | verify T-004-01 | error | 1s | $0.0000 | e3a0367e-edd.. |
| 11 | Worker | F-004 | fix 1 tests | error | 2s | $0.0000 | e1d6fa51-aef.. |
| 12 | Tester | F-004 | verify T-004-01 | error | 1s | $0.0000 | 0465eca8-453.. |
| 13 | Tester | F-001 | verify T-001-01 | ok | 25s | $0.0456 | cbf84dab-3c5.. |
| 14 | Worker | F-001 | fix 1 tests | ok | 27s | $0.0507 | 6ab1934d-918.. |
| 15 | Tester | F-001 | verify T-001-01 | ok | 28s | $0.0537 | 389baa2d-b09.. |
| 16 | Tester | F-002 | verify T-002-01 | ok | 26s | $0.0472 | 5c3f5b6d-933.. |
| 17 | Worker | F-002 | fix 1 tests | ok | 14s | $0.0341 | bd301fc8-a10.. |
| 18 | Tester | F-002 | verify T-002-01 | ok | 23s | $0.0434 | 7127eb4c-3e5.. |
| 19 | Tester | F-003 | verify T-003-01 | ok | 30s | $0.0508 | f0b324f7-730.. |
| 20 | Worker | F-003 | fix 1 tests | ok | 45s | $0.0663 | 4451e986-c0d.. |
| 21 | Tester | F-003 | verify T-003-01 | ok | 30s | $0.0542 | 4cef77a3-f0b.. |
| 22 | Tester | F-004 | verify T-004-01 | ok | 27s | $0.0505 | 7cacb278-e39.. |
| 23 | Worker | F-004 | fix 1 tests | ok | 44s | $0.0820 | 17af7a17-03a.. |
| 24 | Tester | F-004 | verify T-004-01 | ok | 42s | $0.0669 | 94a29b1c-5c0.. |
| 25 | Tester | F-001 | verify T-001-01 | ok | 30s | $0.0448 | 54be31c8-b69.. |
| 26 | Tester | F-002 | verify T-002-01 | ok | 33s | $0.0454 | ecf0c6fc-66b.. |
| 27 | Tester | F-003 | verify T-003-01 | ok | 33s | $0.0531 | 50ebc944-6fb.. |
| 28 | Tester | F-004 | verify T-004-01 | ok | 34s | $0.0537 | 66ff5203-600.. |