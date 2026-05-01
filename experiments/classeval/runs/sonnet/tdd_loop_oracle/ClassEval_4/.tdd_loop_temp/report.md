# TDDLoop Report

| | |
|---|---|
| Result | **ALL PASSED** |
| Change | ClassEval_4 |
| Environment | python_local |
| Start | 2026-04-25 21:14:00 |
| End | 2026-04-25 21:24:52 |
| Duration | 10m51s |
| Iterations | 6 |
| Model | sonnet |
| Cost | $2.1299 |
| Sessions | 24 |

## Features (6/6 passed)

### [PASSED] F-001 Method `add_student(self, name, grade, major)` on class `AssessmentSystem` passes its hidden unit-test suite (oracle ablation arm).

- [✓] **T-001-01** ORACLE TEST RUN for `AssessmentSystem.add_student`.

Write the following Python code to a temp file (e.g. `_oracle_add_student.py`) in the project root and execute `python _oracle_add_student.py` via the Bash tool. The script runs the hidden unit tests for this method.

PASS criteria: process exits with code 0 AND unittest reports `OK` (no failures, no errors).
FAIL criteria: any failure, error, exception, or non-zero exit. Do NOT modify the test code. Do NOT infer the result without actually executing the script.

Script:
```python
import sys, unittest
sys.path.insert(0, '.')

from solution import AssessmentSystem

class AssessmentSystemTestAddStudent(unittest.TestCase):
    def test_add_student(self):
        assessment_system = AssessmentSystem()
        assessment_system.add_student("Alice", 3, "Mathematics")
        self.assertEqual(assessment_system.students["Alice"],
                         {'name': 'Alice', 'grade': 3, 'major': 'Mathematics', 'courses': {}})

    def test_add_student_2(self):
        assessment_system = AssessmentSystem()
        assessment_system.add_student("Alice", 3, "Mathematics")
        assessment_system.add_student("Bob", 2, "Science")
        self.assertEqual(assessment_system.students,
                         {'Alice': {'name': 'Alice', 'grade': 3, 'major': 'Mathematics', 'courses': {}},
                          'Bob': {'name': 'Bob', 'grade': 2, 'major': 'Science', 'courses': {}}})

    def test_add_student_3(self):
        assessment_system = AssessmentSystem()
        assessment_system.add_student("Alice", 3, "Mathematics")
        assessment_system.add_student("Bob", 2, "Science")
        assessment_system.add_student("Charlie", 4, "Chemistry")
        self.assertEqual(assessment_system.students,
                         {'Alice': {'name': 'Alice', 'grade': 3, 'major': 'Mathematics', 'courses': {}},
                          'Bob': {'name': 'Bob', 'grade': 2, 'major': 'Science', 'courses': {}},
                          'Charlie': {'name': 'Charlie', 'grade': 4, 'major': 'Chemistry', 'courses': {}}})

    def test_add_student_4(self):
        assessment_system = AssessmentSystem()
        assessment_system.add_student("Alice", 3, "Mathematics")
        assessment_system.add_student("Bob", 2, "Science")
        assessment_system.add_student("Charlie", 4, "Chemistry")
        assessment_system.add_student("David", 1, "Physics")
        self.assertEqual(assessment_system.students,
                            {'Alice': {'name': 'Alice', 'grade': 3, 'major': 'Mathematics', 'courses': {}},
                                'Bob': {'name': 'Bob', 'grade': 2, 'major': 'Science', 'courses': {}},
                                'Charlie': {'name': 'Charlie', 'grade': 4, 'major': 'Chemistry', 'courses': {}},
                                'David': {'name': 'David', 'grade': 1, 'major': 'Physics', 'courses': {}}})

    def test_add_student_5(self):
        assessment_system = AssessmentSystem()
        assessment_system.add_student("Alice", 3, "Mathematics")
        assessment_system.add_student("Bob", 2, "Science")
        assessment_system.add_student("Charlie", 4, "Chemistry")
        assessment_system.add_student("David", 1, "Physics")
        assessment_system.add_student("Eve", 3, "Mathematics")
        self.assertEqual(assessment_system.students,
                            {'Alice': {'name': 'Alice', 'grade': 3, 'major': 'Mathematics', 'courses': {}},
                                'Bob': {'name': 'Bob', 'grade': 2, 'major': 'Science', 'courses': {}},
                                'Charlie': {'name': 'Charlie', 'grade': 4, 'major': 'Chemistry', 'courses': {}},
                                'David': {'name': 'David', 'grade': 1, 'major': 'Physics', 'courses': {}},
                                'Eve': {'name': 'Eve', 'grade': 3, 'major': 'Mathematics', 'courses': {}}})

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(AssessmentSystemTestAddStudent)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
```

  - All 5 oracle tests ran successfully with exit code 0 and unittest reported OK. The add_student method correctly stores student data with name, grade, major, and empty courses dict.

### [PASSED] F-002 Method `add_course_score(self, name, course, score)` on class `AssessmentSystem` passes its hidden unit-test suite (oracle ablation arm).

- [✓] **T-002-01** ORACLE TEST RUN for `AssessmentSystem.add_course_score`.

Write the following Python code to a temp file (e.g. `_oracle_add_course_score.py`) in the project root and execute `python _oracle_add_course_score.py` via the Bash tool. The script runs the hidden unit tests for this method.

PASS criteria: process exits with code 0 AND unittest reports `OK` (no failures, no errors).
FAIL criteria: any failure, error, exception, or non-zero exit. Do NOT modify the test code. Do NOT infer the result without actually executing the script.

Script:
```python
import sys, unittest
sys.path.insert(0, '.')

from solution import AssessmentSystem

class AssessmentSystemTestAddCourseScore(unittest.TestCase):
    def test_add_course_score(self):
        assessment_system = AssessmentSystem()
        assessment_system.students = {"Alice": {'name': 'Alice', 'grade': 3, 'major': 'Mathematics', 'courses': {}}}
        assessment_system.add_course_score("Alice", "Math", 90)
        self.assertEqual(assessment_system.students["Alice"]["courses"]["Math"], 90)

    def test_add_course_score_2(self):
        assessment_system = AssessmentSystem()
        assessment_system.students["Alice"] = {'name': 'Alice', 'grade': 3, 'major': 'Mathematics', 'courses': {}}
        assessment_system.add_course_score("Alice", "Math", 90)
        self.assertEqual(assessment_system.students["Alice"]["courses"]["Math"], 90)

    def test_add_course_score_3(self):
        assessment_system = AssessmentSystem()
        assessment_system.students["Alice"] = {'name': 'Alice', 'grade': 3, 'major': 'Mathematics', 'courses': {}}
        assessment_system.add_course_score("Alice", "Math", 90)
        assessment_system.add_course_score("Alice", "Science", 80)
        assessment_system.add_course_score("Alice", "Math", 95)
        self.assertEqual(assessment_system.students["Alice"]["courses"]["Math"], 95)
        self.assertEqual(assessment_system.students["Alice"]["courses"]["Science"], 80)

    def test_add_course_score_4(self):
        assessment_system = AssessmentSystem()
        assessment_system.students["Alice"] = {'name': 'Alice', 'grade': 3, 'major': 'Mathematics', 'courses': {}}
        assessment_system.add_course_score("Alice", "Math", 90)
        assessment_system.add_course_score("Alice", "Science", 80)
        assessment_system.add_course_score("Alice", "Math", 95)
        assessment_system.add_course_score("Alice", "Science", 85)
        self.assertEqual(assessment_system.students["Alice"]["courses"]["Math"], 95)
        self.assertEqual(assessment_system.students["Alice"]["courses"]["Science"], 85)

    def test_add_course_score_5(self):
        assessment_system = AssessmentSystem()
        assessment_system.students["Alice"] = {'name': 'Alice', 'grade': 3, 'major': 'Mathematics', 'courses': {}}
        assessment_system.add_course_score("Bob", "Math", 90)
        self.assertEqual(assessment_system.students["Alice"]["courses"], {})

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(AssessmentSystemTestAddCourseScore)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
```

  - All 5 oracle tests for AssessmentSystem.add_course_score passed with exit code 0 and unittest reporting OK. The method correctly adds/updates course scores for existing students and ignores calls for 

### [PASSED] F-003 Method `get_gpa(self, name)` on class `AssessmentSystem` passes its hidden unit-test suite (oracle ablation arm).

- [✓] **T-003-01** ORACLE TEST RUN for `AssessmentSystem.get_gpa`.

Write the following Python code to a temp file (e.g. `_oracle_get_gpa.py`) in the project root and execute `python _oracle_get_gpa.py` via the Bash tool. The script runs the hidden unit tests for this method.

PASS criteria: process exits with code 0 AND unittest reports `OK` (no failures, no errors).
FAIL criteria: any failure, error, exception, or non-zero exit. Do NOT modify the test code. Do NOT infer the result without actually executing the script.

Script:
```python
import sys, unittest
sys.path.insert(0, '.')

from solution import AssessmentSystem

class AssessmentSystemTestGetGPA(unittest.TestCase):
    def test_get_gpa_1(self):
        assessment_system = AssessmentSystem()
        assessment_system.students = {'Alice': {'name': 'Alice', 'grade': 3, 'major': 'Mathematics', 'courses': {'Mathematics': 90, 'Science': 80}}}
        self.assertEqual(assessment_system.get_gpa("Alice"), 85.0)


    # No such student
    def test_get_gpa_2(self):
        assessment_system = AssessmentSystem()
        self.assertEqual(assessment_system.get_gpa('Alice'), None)

    # student don't have any scores
    def test_get_gpa_3(self):
        assessment_system = AssessmentSystem()
        assessment_system.students = {'Alice': {'name': 'Alice', 'grade': 3, 'major': 'Mathematics', 'courses': {}}}
        self.assertEqual(assessment_system.get_gpa('Alice'), None)

    def test_get_gpa_4(self):
        assessment_system = AssessmentSystem()
        assessment_system.students = {'Alice': {'name': 'Alice', 'grade': 3, 'major': 'Mathematics', 'courses': {'Mathematics': 90}}}
        self.assertEqual(assessment_system.get_gpa('Bob'), None)

    def test_get_gpa_5(self):
        assessment_system = AssessmentSystem()
        assessment_system.students = {'Alice': {'name': 'Alice', 'grade': 3, 'major': 'Mathematics', 'courses': {'Mathematics': 90}}}
        self.assertEqual(assessment_system.get_gpa('Alice'), 90.0)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(AssessmentSystemTestGetGPA)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
```

  - All 5 oracle tests for AssessmentSystem.get_gpa passed with exit code 0 and unittest reporting OK. The method correctly returns the average GPA when courses exist, and None for missing students or emp

### [PASSED] F-004 Method `get_all_students_with_fail_course(self)` on class `AssessmentSystem` passes its hidden unit-test suite (oracle ablation arm).

- [✓] **T-004-01** ORACLE TEST RUN for `AssessmentSystem.get_all_students_with_fail_course`.

Write the following Python code to a temp file (e.g. `_oracle_get_all_students_with_fail_course.py`) in the project root and execute `python _oracle_get_all_students_with_fail_course.py` via the Bash tool. The script runs the hidden unit tests for this method.

PASS criteria: process exits with code 0 AND unittest reports `OK` (no failures, no errors).
FAIL criteria: any failure, error, exception, or non-zero exit. Do NOT modify the test code. Do NOT infer the result without actually executing the script.

Script:
```python
import sys, unittest
sys.path.insert(0, '.')

from solution import AssessmentSystem

class AssessmentSystemTestGetAllStudentsWithFailCourse(unittest.TestCase):
    def test_get_all_students_with_fail_course(self):
        assessment_system = AssessmentSystem()
        assessment_system.students = {'Alice': {'name': 'Alice', 'grade': 3, 'major': 'Mathematics', 'courses': {'Mathematics': 90, 'Science': 80}},
                                'Bob': {'name': 'Bob', 'grade': 4, 'major': 'Physics', 'courses': {'Physics': 50}},
                                'Charlie': {'name': 'Charlie', 'grade': 2, 'major': 'Chemistry', 'courses': {'Chemistry': 70}},
                                'David': {'name': 'David', 'grade': 1, 'major': 'Physics', 'courses': {'Physics': 60}},
                                'Eve': {'name': 'Eve', 'grade': 3, 'major': 'Mathematics', 'courses': {'Mathematics': 90}}}
        self.assertEqual(assessment_system.get_all_students_with_fail_course(), ['Bob'])

    def test_get_all_students_with_fail_course_2(self):
        assessment_system = AssessmentSystem()
        assessment_system.students = {'Alice': {'name': 'Alice', 'grade': 3, 'major': 'Mathematics', 'courses': {'Mathematics': 90, 'Science': 80}},
                                'Bob': {'name': 'Bob', 'grade': 4, 'major': 'Physics', 'courses': {'Physics': 70}},
                                'Charlie': {'name': 'Charlie', 'grade': 2, 'major': 'Chemistry', 'courses': {'Chemistry': 70}},
                                'David': {'name': 'David', 'grade': 1, 'major': 'Physics', 'courses': {'Physics': 70}},
                                'Eve': {'name': 'Eve', 'grade': 3, 'major': 'Mathematics', 'courses': {'Mathematics': 90}}}
        self.assertEqual(assessment_system.get_all_students_with_fail_course(), [])

    def test_get_all_students_with_fail_course_3(self):
        assessment_system = AssessmentSystem()
        assessment_system.students = {}
        self.assertEqual(assessment_system.get_all_students_with_fail_course(), [])

    def test_get_all_students_with_fail_course_4(self):
        assessment_system = AssessmentSystem()
        assessment_system.students = {'Alice': {'name': 'Alice', 'grade': 3, 'major': 'Mathematics', 'courses': {}}}
        self.assertEqual(assessment_system.get_all_students_with_fail_course(), [])

    def test_get_all_students_with_fail_course_5(self):
        assessment_system = AssessmentSystem()
        assessment_system.students = {'Alice': {'name': 'Alice', 'grade': 3, 'major': 'Mathematics', 'courses': {'Mathematics': 90, 'Science': 50}},
                                'Bob': {'name': 'Bob', 'grade': 4, 'major': 'Physics', 'courses': {'Physics': 50}},
                                'Charlie': {'name': 'Charlie', 'grade': 2, 'major': 'Chemistry', 'courses': {'Chemistry': 70}},
                                'David': {'name': 'David', 'grade': 1, 'major': 'Physics', 'courses': {'Physics': 70}},
                                'Eve': {'name': 'Eve', 'grade': 3, 'major': 'Mathematics', 'courses': {'Mathematics': 90}}}
        self.assertEqual(assessment_system.get_all_students_with_fail_course(), ['Alice', 'Bob'])

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(AssessmentSystemTestGetAllStudentsWithFailCourse)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
```

  - All 5 oracle tests passed with exit code 0 and unittest reported OK. The get_all_students_with_fail_course method correctly identifies students with any course score below 60.

### [PASSED] F-005 Method `get_course_average(self, course)` on class `AssessmentSystem` passes its hidden unit-test suite (oracle ablation arm).

- [✓] **T-005-01** ORACLE TEST RUN for `AssessmentSystem.get_course_average`.

Write the following Python code to a temp file (e.g. `_oracle_get_course_average.py`) in the project root and execute `python _oracle_get_course_average.py` via the Bash tool. The script runs the hidden unit tests for this method.

PASS criteria: process exits with code 0 AND unittest reports `OK` (no failures, no errors).
FAIL criteria: any failure, error, exception, or non-zero exit. Do NOT modify the test code. Do NOT infer the result without actually executing the script.

Script:
```python
import sys, unittest
sys.path.insert(0, '.')

from solution import AssessmentSystem

class AssessmentSystemTestGetCourseAverage(unittest.TestCase):

    def test_get_course_average_1(self):
        assessment_system = AssessmentSystem()
        assessment_system.students = {'Alice': {'name': 'Alice', 'grade': 3, 'major': 'Mathematics', 'courses': {'Mathematics': 90, 'Science': 80}},
                                'Bob': {'name': 'Bob', 'grade': 4, 'major': 'Physics', 'courses': {'Physics': 90}},
                                'Charlie': {'name': 'Charlie', 'grade': 2, 'major': 'Chemistry', 'courses': {'Chemistry': 70,'Physics': 80}}
                                           }
        self.assertEqual(assessment_system.get_course_average("Physics"), 85.0)

    def test_get_course_average_2(self):
        assessment_system = AssessmentSystem()
        assessment_system.students = {'Alice': {'name': 'Alice', 'grade': 3, 'major': 'Mathematics',
                                                'courses': {'Mathematics': 90, 'Science': 80}},
                                      'Bob': {'name': 'Bob', 'grade': 4, 'major': 'Physics',
                                              'courses': {'Physics': 85}},
                                      'Charlie': {'name': 'Charlie', 'grade': 2, 'major': 'Chemistry',
                                                  'courses': {'Chemistry': 70,'Physics': None }}
                                      }
        self.assertEqual(assessment_system.get_course_average('Physics'), 85)

    def test_get_course_average_3(self):
        assessment_system = AssessmentSystem()
        assessment_system.students = {'Alice': {'name': 'Alice', 'grade': 3, 'major': 'Mathematics',
                                                'courses': {'Mathematics': 90, 'Science': 80}},
                                      'Bob': {'name': 'Bob', 'grade': 4, 'major': 'Physics',
                                              'courses': {'Physics': 85}},
                                      'Charlie': {'name': 'Charlie', 'grade': 2, 'major': 'Chemistry',
                                                  'courses': {'Chemistry': 70, 'Physics': 80}}
                                      }
        self.assertEqual(assessment_system.get_course_average('Computer'), None)

    def test_get_course_average_4(self):
        assessment_system = AssessmentSystem()
        assessment_system.students = {}
        self.assertEqual(assessment_system.get_course_average('Computer'), None)

    def test_get_course_average_5(self):
        assessment_system = AssessmentSystem()
        assessment_system.students = {'Alice': {'name': 'Alice', 'grade': 3, 'major': 'Mathematics',
                                                'courses': {'Mathematics': 90, 'Science': 80}},
                                      'Bob': {'name': 'Bob', 'grade': 4, 'major': 'Physics',
                                              'courses': {'Physics': 85}},
                                      'Charlie': {'name': 'Charlie', 'grade': 2, 'major': 'Chemistry',
                                                  'courses': {'Chemistry': 70, 'Physics': 80}}
                                      }
        self.assertEqual(assessment_system.get_course_average('Mathematics'), 90)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(AssessmentSystemTestGetCourseAverage)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
```

  - All 5 oracle tests passed with exit code 0 and unittest reported OK. The method correctly computes course averages, handles None scores, returns None for missing courses, and handles empty student dic

### [PASSED] F-006 Method `get_top_student(self)` on class `AssessmentSystem` passes its hidden unit-test suite (oracle ablation arm).

- [✓] **T-006-01** ORACLE TEST RUN for `AssessmentSystem.get_top_student`.

Write the following Python code to a temp file (e.g. `_oracle_get_top_student.py`) in the project root and execute `python _oracle_get_top_student.py` via the Bash tool. The script runs the hidden unit tests for this method.

PASS criteria: process exits with code 0 AND unittest reports `OK` (no failures, no errors).
FAIL criteria: any failure, error, exception, or non-zero exit. Do NOT modify the test code. Do NOT infer the result without actually executing the script.

Script:
```python
import sys, unittest
sys.path.insert(0, '.')

from solution import AssessmentSystem

class AssessmentSystemTestGetTopStudent(unittest.TestCase):
    def test_get_top_student(self):
        assessment_system = AssessmentSystem()
        assessment_system.students = {'Alice': {'name': 'Alice', 'grade': 3, 'major': 'Mathematics',
                                                'courses': {'Mathematics': 90}},
                                      'Bob': {'name': 'Bob', 'grade': 4, 'major': 'Physics',
                                              'courses': {'Physics': 85}}
                                      }
        self.assertEqual(assessment_system.get_top_student(), "Alice")

    def test_get_top_student_2(self):
        assessment_system = AssessmentSystem()
        assessment_system.students = {'Alice': {'name': 'Alice', 'grade': 3, 'major': 'Mathematics',
                                                'courses': { }},
                                      'Bob': {'name': 'Bob', 'grade': 4, 'major': 'Physics',
                                              'courses': {'Physics': 85}},
                                      'Charlie': {'name': 'Charlie', 'grade': 2, 'major': 'Chemistry',
                                                  'courses': {'Chemistry': 70, 'Physics': 80}}
                                      }
        self.assertEqual(assessment_system.get_top_student(), "Bob")

    def test_get_top_student_3(self):
        assessment_system = AssessmentSystem()
        assessment_system.students = {}
        self.assertEqual(assessment_system.get_top_student(), None)

    def test_get_top_student_4(self):
        assessment_system = AssessmentSystem()
        assessment_system.students = {'Alice': {'name': 'Alice', 'grade': 3, 'major': 'Mathematics',
                                                'courses': {'Mathematics': 90, 'Science': 60}},
                                      'Bob': {'name': 'Bob', 'grade': 4, 'major': 'Physics',
                                              'courses': {'Physics': 85}},
                                      'Charlie': {'name': 'Charlie', 'grade': 2, 'major': 'Chemistry',
                                                  'courses': {'Chemistry': 70, 'Physics': 80}}
                                      }
        self.assertEqual(assessment_system.get_top_student(), "Bob")

    def test_get_top_student_5(self):
        assessment_system = AssessmentSystem()
        assessment_system.students = {'Alice': {'name': 'Alice', 'grade': 3, 'major': 'Mathematics',
                                                'courses': {'Mathematics': 90, 'Science': 60}},
                                      'Bob': {'name': 'Bob', 'grade': 4, 'major': 'Physics',
                                              'courses': {'Physics': 85}},
                                      'Charlie': {'name': 'Charlie', 'grade': 2, 'major': 'Chemistry',
                                                  'courses': {'Chemistry': 70, 'Physics': 80}},
                                      'David': {'name': 'David', 'grade': 2, 'major': 'Chemistry',
                                                  'courses': {'Chemistry': 70, 'Physics': 80}}
                                      }
        self.assertEqual(assessment_system.get_top_student(), "Bob")

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(AssessmentSystemTestGetTopStudent)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
```

  - All 5 oracle tests passed with exit code 0 and unittest reported OK. The get_top_student method correctly identifies the student with the highest GPA across all test scenarios including empty students

## Sessions (24 total, $2.1299)

| # | Role | Feature | Task | Status | Duration | Cost | Session ID |
|---|------|---------|------|--------|----------|------|------------|
| 1 | Tester | F-001 | verify T-001-01 | ok | 25s | $0.1033 | eefcdab4-a00.. |
| 2 | Worker | F-001 | fix 1 tests | ok | 14s | $0.0688 | b861f487-494.. |
| 3 | Tester | F-001 | verify T-001-01 | ok | 25s | $0.0969 | d425d624-59c.. |
| 4 | Tester | F-002 | verify T-002-01 | ok | 36s | $0.0955 | 80591bb5-0a0.. |
| 5 | Worker | F-002 | fix 1 tests | ok | 15s | $0.0676 | 927a0e47-cd9.. |
| 6 | Tester | F-002 | verify T-002-01 | ok | 26s | $0.0901 | 3d912a81-6ed.. |
| 7 | Tester | F-003 | verify T-003-01 | ok | 25s | $0.0888 | fcf05720-080.. |
| 8 | Worker | F-003 | fix 1 tests | ok | 10s | $0.0650 | f8472074-6b3.. |
| 9 | Tester | F-003 | verify T-003-01 | ok | 23s | $0.0837 | 3cf7ccc7-b71.. |
| 10 | Tester | F-004 | verify T-004-01 | ok | 30s | $0.1083 | 5984737c-574.. |
| 11 | Worker | F-004 | fix 1 tests | ok | 22s | $0.0682 | eafbbe14-244.. |
| 12 | Tester | F-004 | verify T-004-01 | ok | 30s | $0.0981 | 7a3b27a1-920.. |
| 13 | Tester | F-005 | verify T-005-01 | ok | 29s | $0.1015 | ecd3ac43-7c2.. |
| 14 | Worker | F-005 | fix 1 tests | ok | 13s | $0.0698 | 532e0261-d5b.. |
| 15 | Tester | F-005 | verify T-005-01 | ok | 27s | $0.0946 | 64f13828-a0c.. |
| 16 | Tester | F-006 | verify T-006-01 | ok | 30s | $0.1041 | fa896977-81a.. |
| 17 | Worker | F-006 | fix 1 tests | ok | 11s | $0.0692 | ec715066-5e0.. |
| 18 | Tester | F-006 | verify T-006-01 | ok | 28s | $0.0942 | 09eec13b-c2a.. |
| 19 | Tester | F-001 | verify T-001-01 | ok | 26s | $0.0982 | f29ac568-72f.. |
| 20 | Tester | F-002 | verify T-002-01 | ok | 37s | $0.0903 | 02605cc4-c53.. |
| 21 | Tester | F-003 | verify T-003-01 | ok | 22s | $0.0851 | 79e1466d-e01.. |
| 22 | Tester | F-004 | verify T-004-01 | ok | 26s | $0.0982 | 232eafea-f96.. |
| 23 | Tester | F-005 | verify T-005-01 | ok | 33s | $0.0946 | c91dcbec-06f.. |
| 24 | Tester | F-006 | verify T-006-01 | ok | 24s | $0.0953 | cb1afb94-f05.. |