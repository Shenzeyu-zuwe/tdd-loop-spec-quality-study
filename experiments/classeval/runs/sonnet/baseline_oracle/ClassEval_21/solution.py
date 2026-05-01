from datetime import datetime

class Classroom:
    def __init__(self, id):
        self.id = id
        self.courses = []

    def add_course(self, course):
        if course not in self.courses:
            self.courses.append(course)

    def remove_course(self, course):
        if course in self.courses:
            self.courses.remove(course)

    def is_free_at(self, check_time):
        t = datetime.strptime(check_time, '%H:%M')
        for course in self.courses:
            start = datetime.strptime(course['start_time'], '%H:%M')
            end = datetime.strptime(course['end_time'], '%H:%M')
            if start <= t < end:
                return False
        return True

    def check_course_conflict(self, new_course):
        new_start = datetime.strptime(new_course['start_time'], '%H:%M')
        new_end = datetime.strptime(new_course['end_time'], '%H:%M')
        for course in self.courses:
            start = datetime.strptime(course['start_time'], '%H:%M')
            end = datetime.strptime(course['end_time'], '%H:%M')
            if new_start < end and new_end > start:
                return False
        return True