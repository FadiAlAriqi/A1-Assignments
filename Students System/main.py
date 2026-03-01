from models import Student, Classroom
from analytics import (
    top_performing_students,
    lowest_performing_students,
    rank_students,
    grade_distribution
)
from utils import (
    load_students_from_csv,
    save_students_to_csv,
    validate_name,
    validate_student_id,
    validate_grades,
    print_student
)


def main():
    classroom = Classroom()

    while True:
        print("\n===== Classroom Management System =====")
        print("1. Add student")
        print("2. Remove student")
        print("3. Search student")
        print("4. Show classroom average")
        print("5. Show analytics")
        print("6. Load from CSV")
        print("7. Save to CSV")
        print("0. Exit")

        choice = input("Choose an option: ")

        try:
            if choice == "1":
                add_student_flow(classroom)

            elif choice == "2":
                remove_student_flow(classroom)

            elif choice == "3":
                search_student_flow(classroom)

            elif choice == "4":
                print("Classroom Average:", classroom.classroom_average())

            elif choice == "5":
                analytics_flow(classroom)

            elif choice == "6":
                file_path = "data.csv"
                students = load_students_from_csv(file_path)
                for s in students:
                    classroom.add_student(s)
                print("Students loaded successfully.")

            elif choice == "7":
                file_path = "data.csv"
                save_students_to_csv(file_path, classroom.students)
                print("Students saved successfully.")

            elif choice == "0":
                print("Exiting...")
                break

            else:
                print("Invalid choice.")

        except Exception as e:
            print("Error:", e)


def add_student_flow(classroom):
    name = input("Enter name: ")
    student_id = int(input("Enter ID: "))
    grades_input = input("Enter grades separated by comma: ")

    grades = Student.parse_grades(grades_input)

    validate_name(name)
    validate_student_id(student_id)
    validate_grades(grades)

    student = Student(name, student_id, grades)
    classroom.add_student(student)

    print("Student added successfully.")


def remove_student_flow(classroom):
    student_id = int(input("Enter student ID to remove: "))
    classroom.remove_student(student_id)
    print("Student removed.")


def search_student_flow(classroom):
    student_id = int(input("Enter student ID to search: "))
    student = classroom.search_student(student_id)

    if student:
        print_student(student)
    else:
        print("Student not found.")


def analytics_flow(classroom):
    print("\n--- Analytics ---")

    if not classroom.students:
        print("No students available.")
        return

    print("\nTop Student:")
    top_students = top_performing_students(classroom.students)
    if not top_students:
        print("No top students.")
    else:
        for student in top_students:
            print_student(student)

    print("Lowest Student:")
    lowest_students = lowest_performing_students(classroom.students)
    if not lowest_students:
        print("No lowest student.")
    else:
        for student in lowest_students:
            print_student(student)

    print("\nRanking:")
    ranked = rank_students(classroom.students)
    for i, student in enumerate(ranked, start=1):
        print(f"{i}. {student.name} - {student.avg():.2f}")

    print("\nGrade Distribution:")
    distribution = grade_distribution(classroom.students)
    for grade, count in distribution.items():
        print(f"{grade}: {count}")


if __name__ == "__main__":
    main()