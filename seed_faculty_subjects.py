"""
Comprehensive BCA Subject Seeder
=================================
- Assigns 1 subject per semester per faculty for ALL faculty in Dept 15 (Computer Science)
- Covers BCA 6 semesters (3-year program)
- Each faculty member gets 1 unique subject per semester = 6 total subjects
- Subjects named after faculty's specialty / rotating from curriculum pool
- Uses Program 1 (BCA) and Program 24 (BCA NEP-2020)
"""

from app import create_app
from models import db, User, Subject, Program

app = create_app()

# ─── Complete BCA 6-Semester Curriculum Pool ─────────────────────────────────
# One bank per semester; subjects distributed round-robin among faculty
SUBJECT_BANK = {
    1: [
        ("Fundamentals of Computers",           "BCA-1"),
        ("C Programming",                        "BCA-2"),
        ("Digital Logic Design",                 "BCA-3"),
        ("Mathematics for Computing I",          "BCA-4"),
        ("Communication Skills",                 "BCA-5"),
        ("Office Automation Tools",              "BCA-6"),
        ("Environmental Science",                "BCA-7"),
        ("Introduction to Internet",             "BCA-8"),
        ("Web Designing Basics",                 "BCA-9"),
        ("Problem Solving Techniques",           "BCA-10"),
    ],
    2: [
        ("Data Structures Using C",              "BCA-11"),
        ("Object Oriented Programming with C++","BCA-12"),
        ("Operating Systems",                    "BCA-13"),
        ("Mathematics for Computing II",         "BCA-14"),
        ("Computer Graphics",                    "BCA-15"),
        ("Microprocessor Architecture",          "BCA-16"),
        ("Numerical Methods",                    "BCA-17"),
        ("System Analysis and Design",           "BCA-18"),
        ("Business Communication",               "BCA-19"),
        ("Software Testing Fundamentals",        "BCA-20"),
    ],
    3: [
        ("Database Management Systems",          "BCA-21"),
        ("Java Programming",                     "BCA-22"),
        ("Computer Networks",                    "BCA-23"),
        ("Software Engineering",                 "BCA-24"),
        ("Linux Administration",                 "BCA-25"),
        ("VB.Net Programming",                   "BCA-26"),
        ("Discrete Mathematics",                 "BCA-27"),
        ("E-Commerce Technologies",              "BCA-28"),
        ("Information Security Basics",          "BCA-29"),
        ("Project Management",                   "BCA-30"),
    ],
    4: [
        ("Python Programming",                   "BCA-31"),
        ("Web Technologies (HTML/CSS/JS)",       "BCA-32"),
        ("Multimedia and Animation",             "BCA-33"),
        ("Data Warehousing & Mining",            "BCA-34"),
        ("Mobile App Development",               "BCA-35"),
        ("Advanced Java (J2EE)",                 "BCA-36"),
        ("PHP and MySQL",                        "BCA-37"),
        ("Compiler Design",                      "BCA-38"),
        ("Digital Image Processing",             "BCA-39"),
        ("Cyber Security",                       "BCA-40"),
    ],
    5: [
        ("Artificial Intelligence",              "BCA-41"),
        ("Machine Learning Foundations",         "BCA-42"),
        ("Cloud Computing",                      "BCA-43"),
        ("Internet of Things (IoT)",             "BCA-44"),
        ("Big Data Analytics",                   "BCA-45"),
        ("Network Security",                     "BCA-46"),
        ("Advanced Python",                      "BCA-47"),
        ("React JS & Frontend Development",      "BCA-48"),
        ("Software Architecture",                "BCA-49"),
        ("Open Source Technologies",             "BCA-50"),
    ],
    6: [
        ("Project Work & Dissertation",          "BCA-51"),
        ("Emerging Technologies",                "BCA-52"),
        ("Enterprise Resource Planning",         "BCA-53"),
        ("Blockchain & Distributed Systems",     "BCA-54"),
        ("Deep Learning Applications",           "BCA-55"),
        ("DevOps & Containerization",            "BCA-56"),
        ("R Programming for Data Science",       "BCA-57"),
        ("Computer Vision",                      "BCA-58"),
        ("Business Intelligence",                "BCA-59"),
        ("Professional Ethics in Computing",     "BCA-60"),
    ],
}

# Programs to assign subjects to
BCA_PROGRAMS = [1, 24]   # BCA and BCA NEP-2020


def seed_all_faculty_subjects():
    with app.app_context():
        # Get all faculty in Dept 15 (Computer Science)
        faculty_list = User.query.filter_by(
            role='Faculty', department_id=15
        ).order_by(User.id).all()

        print(f"Found {len(faculty_list)} faculty members in Dept 15 (Computer Science)")

        created = 0
        skipped = 0
        total_pool_warn = []

        for prog_id in BCA_PROGRAMS:
            prog = Program.query.get(prog_id)
            if not prog:
                print(f"WARNING: Program {prog_id} not found. Skipping.")
                continue

            print(f"\n{'='*60}")
            print(f"Program: {prog.name} (ID: {prog_id})")
            print(f"{'='*60}")

            for semester in range(1, 7):
                subj_pool = SUBJECT_BANK[semester]
                print(f"\n  --- Semester {semester} ---")

                for i, faculty in enumerate(faculty_list):
                    # Pick a subject from the pool using faculty index (round-robin)
                    pool_idx = i % len(subj_pool)
                    subj_name, subj_code_base = subj_pool[pool_idx]

                    # Make code unique per program/faculty
                    code = f"{subj_code_base}-P{prog_id}-S{semester}-F{faculty.id}"

                    # Check if already assigned
                    existing = Subject.query.filter_by(
                        program_id=prog_id,
                        semester=semester,
                        faculty_id=faculty.id
                    ).first()

                    if existing:
                        print(f"    SKIP  Sem {semester}: {faculty.full_name} already has '{existing.name}'")
                        skipped += 1
                        continue

                    new_sub = Subject(
                        name=subj_name,
                        code=code,
                        program_id=prog_id,
                        semester=semester,
                        faculty_id=faculty.id
                    )
                    db.session.add(new_sub)
                    print(f"    ADD   Sem {semester}: {faculty.full_name:30} -> {subj_name}")
                    created += 1

        db.session.commit()
        print(f"\n{'='*60}")
        print(f"✅  DONE  |  Created: {created}  |  Skipped: {skipped}")
        print(f"Total subjects in DB now: {Subject.query.count()}")
        print(f"{'='*60}")

        # Summary table
        print("\n📋 Faculty Subject Summary (Dept 15):")
        faculty_list = User.query.filter_by(role='Faculty', department_id=15).all()
        for f in faculty_list:
            count = Subject.query.filter_by(faculty_id=f.id).count()
            print(f"   {f.full_name:35} -> {count} subjects total")


if __name__ == "__main__":
    seed_all_faculty_subjects()
