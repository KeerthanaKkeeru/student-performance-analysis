#!/usr/bin/env python3
import sys
import csv

reader = csv.reader(sys.stdin)
header = next(reader, None)

for row in reader:
    if len(row) != 8:
        continue

    student_id = row[0]
    attendance = float(row[1])
    study_hours = float(row[2])
    assignments_done = float(row[3])
    assignments_total = float(row[4])
    quiz_score = float(row[5])
    lms_logins = float(row[6])
    final_marks = float(row[7])

    assignment_score = (
        assignments_done / assignments_total * 100
        if assignments_total > 0 else 0
    )

    study_score = min(study_hours / 20 * 100, 100)
    login_score = min(lms_logins / 30 * 100, 100)

    activity_score = (
        attendance * 0.30
        + assignment_score * 0.25
        + quiz_score * 0.20
        + study_score * 0.15
        + login_score * 0.10
    )

    academic_average = (quiz_score + final_marks) / 2

    if academic_average >= 85:
        category = "Excellent"
    elif academic_average >= 70:
        category = "Good"
    elif academic_average >= 50:
        category = "Average"
    else:
        category = "Needs Improvement"

    support = (
        "Support Suggested"
        if activity_score < 50 or academic_average < 50
        else "No Immediate Support"
    )

    print(
        f"STUDENT\t{student_id}\t{activity_score:.2f}"
        f"\t{academic_average:.2f}\t{category}\t{support}"
    )
    print(f"CATEGORY\t{category}\t1")
