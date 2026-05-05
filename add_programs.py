"""
Script to add Hassan Science College Programs to database
"""
from app import create_app
from models import db, Program, Department

programs_data = [
    ("MSc-Chem", "MSc- Chemistry (CBCS)", "Chemistry"),
    ("BSC- PM", "Physics and Mathematics (PM)", "Science"),
    ("BSC- PC", "Physics and Chemistry (PC)", "Science"),
    ("BSC- PCs", "Physics and Computer Science (PCs)", "Science"),
    ("BSC- PE", "Physics and Electronics (PE)", "Science"),
    ("BSC- MCs", "Mathematics and Compu Science (MCs)", "Science"),
    ("BSC- ME", "Mathematics and Electronics (ME)", "Science"),
    ("BSC- MC", "Mathematics and Chemistry (MC)", "Science"),
    ("BSC- ECs", "Electronics and Computer Science (ECs)", "Science"),
    ("BSC- BZ", "Botany and Zoology (BZ)", "Science"),
    ("BSC- BC", "Botany and Chemistry (BC)", "Science"),
    ("BSC- ZC", "Zoology and Chemistry (ZC)", "Science"),
    ("BSC- BtC", "Biotechnology and Chemistry (BtC)", "Science"),
    ("BSC- BBc", "Botany and Biochemistry (BBc)", "Science"),
    ("BSC- ZBt", "Zoology and Biotechnology (ZBt)", "Science"),
    ("BSC- MbBt", "Microbiology and Biotechnology (MbBt)", "Science"),
    ("BSC- BtBC", "Biotechnology and Biochemistry (BtBC)", "Science"),
    ("BSC- MbBc", "Microbiology and Biochemistry (MbBc)", "Science"),
    ("BSC- MbB", "Microbiology and Botany (MbB)", "Science"),
    ("BSC- BCZ", "Biochemistry and Zoology (BCZ)", "Science"),
    ("BSC- BBT", "Biotechnology and Botany (BBT)", "Science"),
    ("BSC- ZMB", "Zoology and Microbiology (ZMB)", "Science"),
    ("BCA", "BCA (NEP -2020)", "Computer Science")
]

app = create_app('development')

with app.app_context():
    print("Adding programs...")
    
    # Ensure departments exist
    dept_map = {}
    for code, name, dept_name in programs_data:
        if dept_name not in dept_map:
            dept = Department.query.filter_by(name=dept_name).first()
            if not dept:
                dept = Department(name=dept_name)
                db.session.add(dept)
                db.session.commit()
            dept_map[dept_name] = dept.id
            
    added_count = 0
    for code, name, dept_name in programs_data:
        existing = Program.query.filter_by(code=code).first()
        if existing:
            # Update name if changed
            if existing.name != name:
                existing.name = name
            continue
            
        prog = Program(
            code=code,
            name=name,
            department_id=dept_map[dept_name],
            duration_years=2 if "MSc" in code else 3
        )
        db.session.add(prog)
        added_count += 1
        print(f"  Added Program: {name} ({code})")
        
    db.session.commit()
    print(f"\nSuccessfully added {added_count} new programs.")
