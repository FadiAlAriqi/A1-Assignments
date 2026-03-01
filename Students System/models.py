class Student:
    def __init__(self, name: str, student_id: int, grades: list):
        self.name = name
        self.student_id = student_id
        self._validate_grades(grades)
        self._grades = list(grades)

    @classmethod
    def from_csv_row(cls, row):
        name = row[0]
        student_id = int(row[1])
        grades = list(map(int, row[2:])) #[int(x) for x in row[2:]]
        return cls(name, student_id, grades)

    @staticmethod
    def parse_grades(grades_input):
        return [int(g.strip()) for g in grades_input.split(",")]

    def _validate_grades(self, grades):
        if not isinstance(grades, list):
            raise ValueError("Grades must be provided as a list.")

        for grade in grades:
            if not isinstance(grade, (int, float)):
                raise ValueError("Each grade must be a number.")
            if not 0 <= grade <= 100:
                raise ValueError("Grades must be between 0 and 100.")

    @property
    def grades(self):
        return self._grades.copy()

    def avg(self):
        if not self._grades:
            return 0
        return sum(self._grades) / len(self._grades)

    def grade_category(self):
        average = self.avg()

        if 90 <= average <= 100:
            return "A"
        elif 85 <= average < 90:
            return "B"
        elif 80 <= average < 85:
            return "C"
        elif 70 <= average < 80:
            return "D"
        elif 60 <= average < 70:
            return "E"
        else:
            return "F"



class Classroom:
    def __init__(self):
        self._students = []

    @property
    def students(self):
        return self._students.copy()

    def add_student(self, student):
        if not isinstance(student, Student):
            raise ValueError("Only Student objects can be added.")

        if self.search_student(student.student_id):
            raise ValueError("Student with this ID already exists.")

        self._students.append(student)

    def search_student(self, student_id):
        for student in self._students:
            if student.student_id == student_id:
                return student
        return None

    def remove_student(self, student_id):
        student = self.search_student(student_id)

        if not student:
            raise ValueError("Student not found.")

        self._students.remove(student)

    def classroom_average(self):
        if not self._students:
            return 0

        total = sum(student.avg() for student in self._students)
        return total / len(self._students)