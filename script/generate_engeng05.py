import argparse
import csv
import os
import random
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path


@dataclass
class Counts:
    municipalities: int
    schools: int
    class_groups: int
    teachers: int
    students: int
    assignments_per_class: int


def ensure_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)


def deterministic_names(rng: random.Random, prefix: str, n: int) -> list[str]:
    return [f"{prefix}-{i}-{rng.randrange(1000,9999)}" for i in range(1, n + 1)]


def generate_data(seed: int, counts: Counts) -> dict[str, list[dict]]:
    rng = random.Random(seed)

    # Municipalities (≥2)
    municipalities = []
    for i in range(1, counts.municipalities + 1):
        code = f"M{i:02d}"
        municipalities.append({
            "id": i,
            "name": f"Municipality {i}",
            "code": code,
        })

    # Schools (≥6), spread across municipalities
    schools = []
    for i in range(1, counts.schools + 1):
        muni_id = 1 + ((i - 1) % counts.municipalities)
        schools.append({
            "id": i,
            "name": f"High School {i}",
            "municipality_id": muni_id,
            "code": f"SCH{i:03d}",
        })

    # Teachers
    teachers = []
    for i in range(1, counts.teachers + 1):
        school_id = 1 + ((i - 1) % counts.schools)
        teachers.append({
            "id": i,
            "first_name": f"Teacher{i}",
            "last_name": "Eng",
            "email": f"teacher{i}@school.se",
            "school_id": school_id,
        })

    # Students
    students = []
    for i in range(1, counts.students + 1):
        school_id = 1 + ((i - 1) % counts.schools)
        students.append({
            "id": i,
            "first_name": f"Student{i}",
            "last_name": "Last",
            "email": f"student{i}@school.se",
            "school_id": school_id,
        })

    # Courses (ENGENG05 as primary)
    courses = [
        {"id": 1, "name": "Engelska 5", "code": "ENGENG05", "description": "Engelska 5 enligt Gy11"},
    ]

    # Class groups (≥20), all on ENGENG05, spread across schools and teachers
    class_groups = []
    for i in range(1, counts.class_groups + 1):
        school_id = 1 + ((i - 1) % counts.schools)
        teacher_id = 1 + ((i - 1) % counts.teachers)
        class_groups.append({
            "id": i,
            "name": f"ENG5-{i:02d}",
            "course_id": 1,
            "teacher_id": teacher_id,
            "school_id": school_id,
            "academic_year": "2024-2025",
            "code": f"ENG5{i:02d}24",
        })

    # Enrolments: assign each student to one class (round-robin)
    enrolments = []
    enrol_id = 1
    for idx, student in enumerate(students):
        class_id = 1 + (idx % counts.class_groups)
        enrolments.append({
            "id": enrol_id,
            "student_id": student["id"],
            "class_group_id": class_id,
            "enrolment_date": date(2024, 8, 15).isoformat(),
        })
        enrol_id += 1

    # Assignments per class
    base_due = date(2024, 10, 15)
    assignments = []
    asg_id = 1
    for cg in class_groups:
        for j in range(counts.assignments_per_class):
            due = base_due + timedelta(days=7 * j)
            assignments.append({
                "id": asg_id,
                "title": f"ENG5 Essay {j+1}",
                "description": "Write an essay aligned with Gy11 criteria",
                "class_group_id": cg["id"],
                "due_date": due.isoformat(),
                "created_at": (due - timedelta(days=30)).isoformat(),
                "code": f"ASG{asg_id:03d}",
            })
            asg_id += 1

    # Submissions (optional small sample)
    submissions = []
    sub_id = 1
    for e in enrolments[: min(100, len(enrolments))]:
        assignment_id = 1 + ((e["class_group_id"] - 1) * counts.assignments_per_class)
        submissions.append({
            "id": sub_id,
            "assignment_id": assignment_id,
            "student_id": e["student_id"],
            "submitted_at": date(2024, 10, 20).isoformat(),
            "artifact_path": f"artifacts/eng5/{e['student_id']}-{assignment_id}.docx",
            "grade": rng.choice(["A", "B", "C", "D", "E"]),
            "feedback": "Auto-generated sample",
            "code": f"SUB{sub_id:03d}",
        })
        sub_id += 1

    return {
        "municipality": municipalities,
        "school": schools,
        "teacher": teachers,
        "student": students,
        "course": courses,
        "class_group": class_groups,
        "enrolment": enrolments,
        "assignment": assignments,
        "submission": submissions,
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def validate_fk(data: dict[str, list[dict]]) -> None:
    schools = {s["id"] for s in data["school"]}
    municipalities = {m["id"] for m in data["municipality"]}
    teachers = {t["id"] for t in data["teacher"]}
    students = {s["id"] for s in data["student"]}
    courses = {c["id"] for c in data["course"]}
    class_groups = {c["id"] for c in data["class_group"]}

    # school.municipality_id
    for s in data["school"]:
        assert s["municipality_id"] in municipalities, "Invalid municipality_id in school"

    # teacher.school_id, student.school_id
    for t in data["teacher"]:
        assert t["school_id"] in schools, "Invalid school_id in teacher"
    for s in data["student"]:
        assert s["school_id"] in schools, "Invalid school_id in student"

    # class_group course/teacher/school
    for cg in data["class_group"]:
        assert cg["course_id"] in courses, "Invalid course_id in class_group"
        assert cg["teacher_id"] in teachers, "Invalid teacher_id in class_group"
        assert cg["school_id"] in schools, "Invalid school_id in class_group"

    # enrolment student/class_group
    for e in data["enrolment"]:
        assert e["student_id"] in students, "Invalid student_id in enrolment"
        assert e["class_group_id"] in class_groups, "Invalid class_group_id in enrolment"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate ENGENG05 deterministic dataset")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=str, default=str(Path(__file__).parent / "output"))
    parser.add_argument("--municipalities", type=int, default=2)
    parser.add_argument("--schools", type=int, default=6)
    parser.add_argument("--class-groups", type=int, default=20)
    parser.add_argument("--teachers", type=int, default=8)
    parser.add_argument("--students", type=int, default=200)
    parser.add_argument("--assignments-per-class", type=int, default=1)
    args = parser.parse_args()

    counts = Counts(
        municipalities=max(2, args.municipalities),
        schools=max(6, args.schools),
        class_groups=max(20, args["class_groups"] if isinstance(args, dict) else args.class_groups),
        teachers=max(6, args.teachers),
        students=max(60, args.students),
        assignments_per_class=max(1, args.assignments_per_class),
    )

    output_dir = Path(args.output)
    ensure_output_dir(output_dir)

    data = generate_data(args.seed, counts)
    validate_fk(data)

    for name, rows in data.items():
        write_csv(output_dir / f"{name}.csv", rows)

    print("OK: generated CSVs in", os.fspath(output_dir))


if __name__ == "__main__":
    main()


