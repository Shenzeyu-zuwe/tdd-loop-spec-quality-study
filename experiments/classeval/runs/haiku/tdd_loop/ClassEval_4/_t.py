import sys
sys.path.insert(0, '.')

from solution import AssessmentSystem
system = AssessmentSystem()
system.add_course_score('student 1', 'Society', 59)
print(system.get_all_students_with_fail_course())
