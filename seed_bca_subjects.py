"""
Seed BCA subjects for all 6 semesters across both BCA programs.
- BCA (program_id=1, dept 4: B.Sc Computer Science)  
- BCA NEP-2020 (program_id=24, dept 15: Computer Science)

Assigns 2 Computer Applications subjects per semester per program,
distributed among faculty in Dept 15 (Computer Science).
"""

from app import create_app
from models import db, User, Subject, Program

app = create_app()

# --- BCA Curriculum (6 semesters, 2 subjects each) ---
BCA_CURRICULUM = {
    1: [
        {"name": "Fundamentals of Computers",        "code": "BCA101"},
        {"name": "C Programming",                    "code": "BCA102"},
    ],
    2: [
        {"name": "Data Structures using C",          "code": "BCA201"},
        {"name": "Digital Electronics",              "code": "BCA202"},
    ],
    3: [
        {"name": "Object Oriented Programming with C++", "code": "BCA301"},
        {"name": "Database Management Systems",      "code": "BCA302"},
    ],
    4: [
        {"name": "Java Programming",                 "code": "BCA401"},
        {"name": "Software Engineering",             "code": "BCA402"},
    ],
    5: [
        {"name": "Web Technologies",                 "code": "BCA501"},
        {"name": "Python Programming",               "code": "BCA502"},
    ],
    6: [
        {"name": "Cloud Computing & Networking",     "code": "BCA601"},
        {"name": "Artificial Intelligence",          "code": "BCA602"},
    ],
}

# Faculty in Dept 15 (Computer Science) to assign subjects to
# (IDs from: 52, 53, 54, 55, 56, 57, 89, 90, 91, 92, 93, 94, 95, 96, 97)
FACULTY_IDS_DEPT15 = [
    52, 53, 54, 55, 56, 57, 89, 90, 91, 92,
    93, 94, 95, 96, 97, 98, 99, 100, 101, 102,
    103, 104
]

# Programs to seed
PROGRAMS = [
    {"id": 1,  "name": "Bachelor of Computer Applications"},
    {"id": 24, "name": "BCA (NEP-2020)"},
]

def seed_subjects():
    with app.app_context():
        print("Starting BCA subject seeding...")

        # Validate faculty exist
        valid_faculty = []
        for fid in FACULTY_IDS_DEPT15:
            u = User.query.get(fid)
            if u and u.role == 'Faculty':
                valid_faculty.append(fid)

        print(f"Found {len(valid_faculty)} valid faculty members")
        if not valid_faculty:
            print("ERROR: No valid faculty found!")
            return

        faculty_idx = 0
        created = 0
        skipped = 0

        for prog in PROGRAMS:
            prog_obj = Program.query.get(prog["id"])
            if not prog_obj:
                print(f"WARNING: Program {prog['id']} not found, skipping.")
                continue

            print(f"\n--- Seeding subjects for: {prog['name']} (ID: {prog['id']}) ---")

            for semester, subjects in BCA_CURRICULUM.items():
                for subj in subjects:
                    # Build a unique code per program
                    code = f"{subj['code']}-P{prog['id']}"

                    # Check if already exists
                    existing = Subject.query.filter_by(
                        code=code,
                        program_id=prog["id"],
                        semester=semester
                    ).first()

                    if existing:
                        print(f"  SKIP (exists): Sem {semester} - {subj['name']}")
                        skipped += 1
                        continue

                    # Assign faculty round-robin
                    assigned_faculty_id = valid_faculty[faculty_idx % len(valid_faculty)]
                    faculty_idx += 1

                    new_subject = Subject(
                        name=subj["name"],
                        code=code,
                        program_id=prog["id"],
                        semester=semester,
                        faculty_id=assigned_faculty_id
                    )
                    db.session.add(new_subject)

                    faculty_name = User.query.get(assigned_faculty_id).full_name
                    print(f"  ADD: Sem {semester} - {subj['name']} -> Faculty: {faculty_name}")
                    created += 1

        db.session.commit()
        print(f"\n✅ Done! Created: {created}, Skipped (already existed): {skipped}")
        print(f"Total subjects now: {Subject.query.count()}")


if __name__ == "__main__":
    seed_subjects()
