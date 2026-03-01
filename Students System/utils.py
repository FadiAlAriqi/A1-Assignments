import csv
from models import Student

def load_students_from_csv(file_path):
    students = []

    with open(file_path, newline="", encoding="utf-8") as file:
        reader = csv.reader(file)

        for row in reader:
            student = Student.from_csv_row(row)
            students.append(student)

    return students

def save_students_to_csv(file_path, students):
    with open(file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        for student in students:
            row = [student.name, student.student_id] + student.grades
            writer.writerow(row)




def validate_name(name):
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Name must be a non-empty string.")


def validate_student_id(student_id):
    if not isinstance(student_id, int):
        raise ValueError("Student ID must be an integer.")


def validate_grades(grades):
    if not isinstance(grades, list):
        raise ValueError("Grades must be a list.")

    for grade in grades:
        if not isinstance(grade, (int, float)):
            raise ValueError("All grades must be numbers.")
        if not (0 <= grade <= 100):
            raise ValueError("Grades must be between 0 and 100.")





def print_student(student):
    print(f"Name: {student.name}")
    print(f"ID: {student.student_id}")
    print(f"Grades: {student.grades}")
    print(f"Average: {student.avg():.2f}")
    print(f"Category: {student.grade_category()}")
    print("-" * 30)