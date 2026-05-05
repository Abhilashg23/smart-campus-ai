"""
Script to add Chanakya University faculty data to database
"""
from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash
from datetime import datetime

app = create_app('development')

with app.app_context():
    print("Adding Chanakya University faculty to database...")
    
    # Faculty data from website
    faculty_data = [
        # Professors of Eminence
        {'name': 'Prof. K. V. Raju', 'role': 'faculty', 'title': 'Professor Emeritus', 'qualification': 'Ph.D., Sardar Patel University', 'department': 'School of Arts, Humanities and Social Sciences'},
        {'name': 'Prof. G. Raghuram', 'role': 'faculty', 'title': 'Professor Emeritus', 'qualification': 'Ph.D., Northwestern University, USA', 'department': 'School of Management Sciences'},
        {'name': 'Prof. S. S. Iyengar', 'role': 'faculty', 'title': 'Honorary Professor', 'qualification': 'Ph.D., Michigan State University, USA', 'department': 'School of Engineering'},
        {'name': 'Prof. P. Ishwara Bhat', 'role': 'faculty', 'title': 'Honorary Distinguished Professor', 'qualification': 'Ph.D., Mysore University', 'department': 'School of Law, Governance and Public Policy'},
        
        # Professors
        {'name': 'Prof. Yashavantha Dongre', 'role': 'faculty', 'title': 'Vice-Chancellor', 'qualification': 'Ph.D., Mysore University', 'department': 'Administration'},
        {'name': 'Prof. H.S. Subramanya', 'role': 'faculty', 'title': 'Pro Vice-Chancellor, Dean', 'qualification': 'Ph.D., IISc Bengaluru; Post-doc, Oxford', 'department': 'School of Biosciences'},
        {'name': 'Prof. Sushant T. Joshi', 'role': 'faculty', 'title': 'Registrar & Professor', 'qualification': 'Ph.D., Rani Channamma University', 'department': 'School of Management Sciences'},
        {'name': 'Prof. Sandeep Nair', 'role': 'faculty', 'title': 'Professor & Dean', 'qualification': 'M.A. Economics, Ph.D. Management', 'department': 'School of Arts, Humanities and Social Sciences'},
        {'name': 'Prof. Shrinivas S. Balli', 'role': 'faculty', 'title': 'Dean, Student Affairs', 'qualification': 'Ph.D.', 'department': 'Student Affairs'},
        {'name': 'Prof. H. S. Ashok', 'role': 'faculty', 'title': 'Professor of Psychology', 'qualification': 'Ph.D., Bangalore University', 'department': 'School of Arts, Humanities and Social Sciences'},
        {'name': 'Prof. Chetan Basavaraj Singai', 'role': 'faculty', 'title': 'Professor & Dean', 'qualification': 'Ph.D., MAHE, NIAS Bengaluru', 'department': 'School of Law, Governance and Public Policy'},
        {'name': 'Prof. Ashwin Kumar A. P.', 'role': 'faculty', 'title': 'Dean, Academics', 'qualification': 'Ph.D., Manipal University', 'department': 'Academics'},
        {'name': 'Prof. Anilkumar G. Garag', 'role': 'faculty', 'title': 'Professor of Management', 'qualification': 'Ph.D., Goa University', 'department': 'School of Management Sciences'},
        {'name': 'Prof. Bhavani M. R.', 'role': 'faculty', 'title': 'Registrar Evaluation & Professor', 'qualification': 'Ph.D., Shivaji University', 'department': 'Evaluation'},
        {'name': 'Prof. Maruthi R. Suresh', 'role': 'faculty', 'title': 'Professor of Management', 'qualification': 'Ph.D., M. S. University of Baroda', 'department': 'School of Management Sciences'},
        {'name': 'Prof. Ramakrishna Pejathaya', 'role': 'faculty', 'title': 'Professor', 'qualification': 'Ph.D., Rastriya Sanskrit Vidyapeetha', 'department': 'School of Arts, Humanities and Social Sciences'},
        {'name': 'Prof. Dileep Prabhakar Jatkar', 'role': 'faculty', 'title': 'Professor', 'qualification': 'Ph.D., Institute of Physics, Bhubaneswar', 'department': 'School of Mathematics and Natural Sciences'},
        
        # Assistant Professors
        {'name': 'Capt. Chaitanya Ramesh', 'role': 'faculty', 'title': 'Assistant Professor', 'qualification': 'M.Phil., Periyar University', 'department': 'School of Mathematics and Natural Sciences'},
        {'name': 'Dr. Charu Ratna Dubey', 'role': 'faculty', 'title': 'Assistant Professor of International Relations', 'qualification': 'Ph.D., JNU, New Delhi', 'department': 'School of Arts, Humanities and Social Sciences'},
        {'name': 'Sri Naresh Dixit P. S.', 'role': 'faculty', 'title': 'Assistant Professor', 'qualification': 'M.Tech., VTU, Belagavi', 'department': 'School of Engineering'},
        {'name': 'Dr. Priyadarshan Kinatukara', 'role': 'faculty', 'title': 'Assistant Professor', 'qualification': 'Ph.D., CSIR-CCMB', 'department': 'School of Biosciences'},
        {'name': 'Dr. Saurav Sarmah', 'role': 'faculty', 'title': 'Assistant Professor of International Relations', 'qualification': 'Ph.D., JNU, New Delhi', 'department': 'School of Arts, Humanities and Social Sciences'},
        {'name': 'Sri Ajay Chandra', 'role': 'faculty', 'title': 'Assistant Professor of Psychology', 'qualification': 'M.Sc., Bangalore University', 'department': 'School of Arts, Humanities and Social Sciences'},
        {'name': 'Kum. Anusha M. Virupannavar', 'role': 'faculty', 'title': 'Assistant Professor of Law', 'qualification': 'LL.M., Karnataka State Law University', 'department': 'School of Law, Governance and Public Policy'},
        {'name': 'Dr. Shilpee Jain', 'role': 'faculty', 'title': 'Assistant Professor', 'qualification': 'Ph.D., IIT Kanpur', 'department': 'School of Biosciences'},
        {'name': 'Sri Praphulla Chandra N.', 'role': 'faculty', 'title': 'Assistant Professor of Commerce', 'qualification': 'M.Com., M.B.A., Annamalai University', 'department': 'School of Management Sciences'},
        {'name': 'Dr. Madhuri Mukhopadhyay', 'role': 'faculty', 'title': 'Assistant Professor', 'qualification': 'Ph.D., IACS, Kolkata', 'department': 'School of Mathematics and Natural Sciences'},
        {'name': 'Dr. Sirshendu Ghosh', 'role': 'faculty', 'title': 'Assistant Professor', 'qualification': 'Ph.D., IACS, Kolkata', 'department': 'School of Mathematics and Natural Sciences'},
        {'name': 'Dr. Vijay V.', 'role': 'faculty', 'title': 'Assistant Professor', 'qualification': 'Ph.D., IIT Madras', 'department': 'School of Engineering'},
        {'name': 'Dr. Deepthi Hebbale', 'role': 'faculty', 'title': 'Assistant Professor', 'qualification': 'Ph.D., IISc, Bengaluru', 'department': 'School of Biosciences'},
        {'name': 'Dr. Ashish Kumar Shukla', 'role': 'faculty', 'title': 'Assistant Professor', 'qualification': 'Ph.D., IIITDM, Jabalpur', 'department': 'School of Engineering'},
        {'name': 'Sri Hemanth N. V.', 'role': 'faculty', 'title': 'Assistant Professor of Physical Education', 'qualification': 'M.P.Ed., Mangalore University', 'department': 'Physical Education and Sports'},
    ]
    
    # Get department IDs
    from models import Department
    dept_map = {}
    for dept in Department.query.all():
        dept_map[dept.name] = dept.id
    
    added_count = 0
    for fac in faculty_data:
        # Create username from name
        username = fac['name'].lower().replace('prof. ', '').replace('dr. ', '').replace('sri ', '').replace('kum. ', '').replace('capt. ', '').replace(' ', '_').replace('.', '')
        
        # Check if user already exists
        existing = User.query.filter_by(username=username).first()
        if existing:
            print(f"  Skipped: {fac['name']} (already exists)")
            continue
        
        # Find department ID
        dept_id = None
        for dept_name, did in dept_map.items():
            if fac['department'] in dept_name or dept_name in fac['department']:
                dept_id = did
                break
        
        # Create faculty user
        user = User(
            username=username,
            email=f"{username}@chanakyauniversity.edu.in",
            password_hash=generate_password_hash('Faculty@123'),
            full_name=fac['name'],
            role='faculty',
            department_id=dept_id,
            is_active=True
        )
        db.session.add(user)
        added_count += 1
        print(f"  Added: {fac['name']} - {fac['title']}")
    
    db.session.commit()
    
    print(f"\n{'='*60}")
    print(f"Total faculty added: {added_count}")
    print(f"{'='*60}")
    print("\nFaculty data added successfully!")
    print("\nYou can now ask the chatbot:")
    print("- 'Tell me about Prof. Sandeep Nair'")
    print("- 'Who is the Dean of Engineering?'")
    print("- 'List all faculty in Biosciences'")
