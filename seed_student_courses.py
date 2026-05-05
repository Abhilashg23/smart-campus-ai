"""
Student Course Allocation Seeder
=================================
Step 1: Create subjects for programs that have no subjects yet
         (BSc-PMCs prog 25, Physics+CS prog 5, etc.)
Step 2: Enrol every student into ALL subjects of their
         program + semester by creating InternalMarks records
         (marks = NULL until faculty enters them)
"""

from app import create_app
from models import db, User, Subject, Program, Department, InternalMarks

app = create_app()

# ── Subject banks for extra programs ─────────────────────────────────────────
# Program 5  = Physics and Computer Science (PCs)
PHYS_CS_SUBJECTS = {
    1: [("Mechanics and Properties of Matter",  "PCS-101"), ("Fundamentals of Computers",       "PCS-102"), ("Calculus",                         "PCS-103")],
    2: [("Waves and Optics",                     "PCS-201"), ("C Programming",                    "PCS-202"), ("Algebra and Geometry",             "PCS-203")],
    3: [("Electricity and Magnetism",            "PCS-301"), ("Data Structures",                  "PCS-302"), ("Statistical Methods",              "PCS-303")],
    4: [("Modern Physics",                       "PCS-401"), ("Database Management Systems",      "PCS-402"), ("Numerical Analysis",               "PCS-403")],
    5: [("Solid State Physics",                  "PCS-501"), ("Object Oriented Programming",      "PCS-502"), ("Operations Research",              "PCS-503")],
    6: [("Nuclear Physics",                      "PCS-601"), ("Web Technologies",                 "PCS-602"), ("Project Work",                     "PCS-603")],
}

# Program 25 = BSc-PMCs (Physics, Mathematics, Computer Science)
BSC_PMCS_SUBJECTS = {
    1: [("Mechanics",                           "PMC-101"), ("Algebra",                           "PMC-102"), ("Fundamentals of Computers",       "PMC-103")],
    2: [("Thermodynamics",                      "PMC-201"), ("Calculus",                          "PMC-202"), ("C Programming",                   "PMC-203")],
    3: [("Optics",                              "PMC-301"), ("Differential Equations",            "PMC-302"), ("Data Structures",                 "PMC-303")],
    4: [("Electricity & Magnetism",             "PMC-401"), ("Numerical Analysis",               "PMC-402"), ("DBMS",                            "PMC-403")],
    5: [("Modern Physics",                      "PMC-501"), ("Linear Algebra",                   "PMC-502"), ("Python Programming",              "PMC-503")],
    6: [("Nuclear & Particle Physics",          "PMC-601"), ("Operations Research",              "PMC-602"), ("Project Work & Viva",             "PMC-603")],
}

# Fallback subjects for any other program (generic BSc)
GENERIC_BSC_SUBJECTS = {
    1: [("Foundation Course I",                 "GEN-101"), ("English Communication",            "GEN-102"), ("Environmental Science",           "GEN-103")],
    2: [("Foundation Course II",                "GEN-201"), ("Computer Basics",                  "GEN-202"), ("Statistical Methods",             "GEN-203")],
    3: [("Core Paper I",                        "GEN-301"), ("Core Paper II",                    "GEN-302"), ("Allied Subject I",                "GEN-303")],
    4: [("Core Paper III",                      "GEN-401"), ("Core Paper IV",                    "GEN-402"), ("Allied Subject II",               "GEN-403")],
    5: [("Core Paper V",                        "GEN-501"), ("Elective I",                       "GEN-502"), ("Practical / Lab",                 "GEN-503")],
    6: [("Core Paper VI",                       "GEN-601"), ("Elective II",                      "GEN-602"), ("Project Work",                    "GEN-603")],
}

EXTRA_PROGRAM_BANKS = {
    5:  PHYS_CS_SUBJECTS,
    25: BSC_PMCS_SUBJECTS,
}

# Default faculty to assign subjects to when no dept-specific faculty exists
# (Dr. Jane Smith is in dept 4 which covers BCA)
DEFAULT_FACULTY_IDS = [3]   # Dr. Jane Smith

# CS dept faculty pool for BCA-adjacent programs
CS_FACULTY_IDS = [52, 53, 54, 55, 56, 57, 89, 90, 91, 92, 93]


def get_or_create_subjects(prog_id: int, semester: int, subject_bank: dict, faculty_pool: list) -> list:
    """Return subjects for program+semester, creating them if missing."""
    existing = Subject.query.filter_by(program_id=prog_id, semester=semester).all()
    if existing:
        return existing

    bank = subject_bank.get(semester, GENERIC_BSC_SUBJECTS.get(semester, []))
    created = []
    for i, (name, code_base) in enumerate(bank):
        code = f"{code_base}-P{prog_id}"
        faculty_id = faculty_pool[i % len(faculty_pool)]
        subj = Subject(name=name, code=code, program_id=prog_id,
                       semester=semester, faculty_id=faculty_id)
        db.session.add(subj)
        created.append(subj)
    db.session.flush()   # get IDs without committing
    return created


def enrol_student_in_subjects(student_id: int, subjects: list) -> tuple:
    """Create InternalMarks rows (marks=NULL) for each subject. Returns (created, skipped)."""
    created = skipped = 0
    for subj in subjects:
        exists = InternalMarks.query.filter_by(
            student_id=student_id, subject_id=subj.id
        ).first()
        if exists:
            skipped += 1
        else:
            db.session.add(InternalMarks(
                student_id=student_id,
                subject_id=subj.id,
                marks=None,
                max_marks=100.0
            ))
            created += 1
    return created, skipped


def run():
    with app.app_context():
        students = User.query.filter_by(role='Student', is_active=True).all()
        print(f"Found {len(students)} active students\n")

        total_subj_created = 0
        total_enrol_created = 0
        total_enrol_skipped = 0

        for student in students:
            if not student.program_id or not student.semester:
                print(f"  SKIP {student.full_name} — no program/semester set")
                continue

            prog = Program.query.get(student.program_id)
            prog_name = prog.name if prog else f"prog#{student.program_id}"

            # Pick the right subject bank and faculty pool
            bank = EXTRA_PROGRAM_BANKS.get(student.program_id, GENERIC_BSC_SUBJECTS)
            if student.program_id in (1, 24):
                faculty_pool = CS_FACULTY_IDS
            else:
                faculty_pool = DEFAULT_FACULTY_IDS

            # Ensure subjects exist for this program + semester
            subjects = get_or_create_subjects(
                student.program_id, student.semester, bank, faculty_pool
            )
            new_subjs = [s for s in subjects if s.id is None]  # flushed but check
            # Re-query to get committed ones
            db.session.flush()
            subjects = Subject.query.filter_by(
                program_id=student.program_id, semester=student.semester
            ).all()

            # Enrol student
            created, skipped = enrol_student_in_subjects(student.id, subjects)
            total_enrol_created += created
            total_enrol_skipped += skipped

            print(f"  ✅ {student.full_name:30} | {prog_name} Sem {student.semester} "
                  f"| {len(subjects)} subjects | +{created} enrolled ({skipped} existed)")

        db.session.commit()

        print(f"\n{'='*65}")
        print(f"DONE")
        print(f"  New enrolment records : {total_enrol_created}")
        print(f"  Already existed       : {total_enrol_skipped}")
        print(f"  Total InternalMarks   : {InternalMarks.query.count()}")
        print(f"  Total Subjects in DB  : {Subject.query.count()}")
        print(f"{'='*65}")

        # Verification
        print("\n📋 Student Enrolment Summary:")
        for student in User.query.filter_by(role='Student', is_active=True).all():
            cnt = InternalMarks.query.filter_by(student_id=student.id).count()
            prog = Program.query.get(student.program_id) if student.program_id else None
            print(f"   {student.full_name:35} | Sem {student.semester} | {cnt} subject(s) enrolled")


if __name__ == "__main__":
    run()
