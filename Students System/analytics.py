def top_performing_students(students):
    if not students:
        return []

    highest = max(student.avg() for student in students)

    return [student for student in students if student.avg() == highest]

def lowest_performing_students(students):
    if not students:
        return []

    lowest = min(student.avg() for student in students)

    highest = max(student.avg() for student in students)

    if lowest == highest:
        return []

    return [student for student in students if student.avg() == lowest]


def rank_students(students):
    return sorted(students, key=lambda student: student.avg(), reverse=True)


def grade_distribution(students):
    distribution = {}

    for student in students:
        category = student.grade_category()

        if category not in distribution:
            distribution[category] = 1
        else:
            distribution[category] += 1

    return distribution