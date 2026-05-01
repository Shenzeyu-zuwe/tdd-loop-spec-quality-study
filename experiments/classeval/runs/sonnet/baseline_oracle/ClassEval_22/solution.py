class ClassRegistrationSystem:
    def __init__(self):
        self.students = []
        self.students_registration_classes = {}

    def register_student(self, student):
        if student in self.students:
            return 0
        self.students.append(student)
        return 1

    def register_class(self, student_name, class_name):
        if student_name not in self.students_registration_classes:
            self.students_registration_classes[student_name] = []
        self.students_registration_classes[student_name].append(class_name)
        return self.students_registration_classes[student_name]

    def get_students_by_major(self, major):
        return [s["name"] for s in self.students if s["major"] == major]

    def get_all_major(self):
        seen = []
        for s in self.students:
            if s["major"] not in seen:
                seen.append(s["major"])
        return seen

    def get_most_popular_class_in_major(self, major):
        students_in_major = self.get_students_by_major(major)
        counts = {}
        for name in students_in_major:
            for cls in self.students_registration_classes.get(name, []):
                counts[cls] = counts.get(cls, 0) + 1
        return max(counts, key=lambda c: counts[c])