"""
Complete faculty database update with all details from Chanakya University
"""
from app import create_app
from models import db, User, Department
from werkzeug.security import generate_password_hash

app = create_app('development')

with app.app_context():
    print("="*70)
    print("Adding ALL Chanakya University Faculty with Complete Details")
    print("="*70)
    
    # Complete faculty data with all details
    all_faculty = [
        # Professors of Eminence
        {'name': 'Prof. K. V. Raju', 'title': 'Professor Emeritus', 'qualification': 'Ph.D., Sardar Patel University, Gujarat', 'department': 'Arts'},
        {'name': 'Prof. G. Raghuram', 'title': 'Professor Emeritus', 'qualification': 'Ph.D., Northwestern University, USA', 'department': 'Management'},
        {'name': 'Prof. S. S. Iyengar', 'title': 'Honorary Professor', 'qualification': 'Ph.D., Michigan State University, USA', 'department': 'Engineering'},
        {'name': 'Prof. P. Ishwara Bhat', 'title': 'Honorary Distinguished Professor', 'qualification': 'Ph.D., Mysore University', 'department': 'Law'},
        
        # Professors
        {'name': 'Prof. Yashavantha Dongre', 'title': 'Vice-Chancellor', 'qualification': 'Ph.D., Mysore University', 'department': 'Administration'},
        {'name': 'Prof. H.S. Subramanya', 'title': 'Pro Vice-Chancellor, Dean', 'qualification': 'Ph.D., IISc Bengaluru; Post-doc, Oxford University, UK', 'department': 'Biosciences'},
        {'name': 'Prof. Sushant T. Joshi', 'title': 'Registrar & Professor', 'qualification': 'Ph.D., Rani Channamma University, Belagavi', 'department': 'Management'},
        {'name': 'Prof. Sandeep Nair', 'title': 'Professor & Dean', 'qualification': 'M.A. Economics, Ph.D. Management', 'department': 'Arts'},
        {'name': 'Prof. Shrinivas S. Balli', 'title': 'Dean, Student Affairs', 'qualification': 'Ph.D.', 'department': 'Student Affairs'},
        {'name': 'Prof. H. S. Ashok', 'title': 'Professor of Psychology', 'qualification': 'Ph.D., Bangalore University', 'department': 'Arts'},
        {'name': 'Prof. Chetan Basavaraj Singai', 'title': 'Professor & Dean, Academic Lead', 'qualification': 'Ph.D., MAHE, NIAS, Bengaluru', 'department': 'Law'},
        {'name': 'Prof. Ashwin Kumar A. P.', 'title': 'Dean, Academics', 'qualification': 'Ph.D., Manipal University', 'department': 'Academics'},
        {'name': 'Prof. Anilkumar G. Garag', 'title': 'Professor of Management', 'qualification': 'Ph.D., Goa University', 'department': 'Management'},
        {'name': 'Prof. Bhavani M. R.', 'title': 'Registrar Evaluation & Professor', 'qualification': 'Ph.D., Shivaji University, Kolhapur', 'department': 'Evaluation'},
        {'name': 'Prof. Maruthi R. Suresh', 'title': 'Professor of Management', 'qualification': 'Ph.D., M. S. University of Baroda', 'department': 'Management'},
        {'name': 'Prof. Ramakrishna Pejathaya', 'title': 'Professor', 'qualification': 'Ph.D., Rastriya Sanskrit Vidyapeetha, Tirupati', 'department': 'Arts'},
        {'name': 'Prof. Dileep Prabhakar Jatkar', 'title': 'Professor', 'qualification': 'Ph.D., Institute of Physics, Bhubaneswar; M.Sc., IIT Mumbai', 'department': 'Mathematics'},
        
        # Associate Professors
        {'name': 'Dr. Vinayachandra Banavathy', 'title': 'Director, Centre for IKS; Associate Professor', 'qualification': 'Ph.D., Pondicherry University', 'department': 'Arts'},
        {'name': 'Dr. Rajesh Aruchamy', 'title': 'Associate Professor', 'qualification': 'Ph.D., Bharathiar University, Coimbatore', 'department': 'Arts'},
        {'name': 'Dr. Pradeep Kumar', 'title': 'Associate Professor', 'qualification': 'Ph.D., Mewar University, Chittorgarh', 'department': 'Law'},
        {'name': 'Dr. Vinayak Rajat Bhat', 'title': 'Associate Professor', 'qualification': 'Ph.D., Rastriya Sanskrit Samsthana, Sringeri', 'department': 'Arts'},
        {'name': 'Dr. Krishna Kurthkoti', 'title': 'Associate Professor', 'qualification': 'Ph.D., IISc Bengaluru; Post-doc, Rutgers University', 'department': 'Biosciences'},
        {'name': 'Dr. Naveen Bhat', 'title': 'Associate Professor', 'qualification': 'Ph.D., Central Sanskrit University, Delhi', 'department': 'Arts'},
        {'name': 'Dr. Poonam Purohit', 'title': 'Associate Professor', 'qualification': 'Ph.D., Banasthali University, Rajasthan; Post-doc, IIMB', 'department': 'Management'},
        {'name': 'Dr. Shubhada Hegde', 'title': 'Associate Professor', 'qualification': 'Ph.D., CDFD Hyderabad; Post-doc, IISc Bengaluru', 'department': 'Biosciences'},
        {'name': 'Dr. Rajesh Kumar Prasad', 'title': 'Associate Professor', 'qualification': 'Ph.D., IIT Kanpur', 'department': 'Mathematics'},
        {'name': 'Dr. Sumi S', 'title': 'Associate Professor', 'qualification': 'Ph.D., SCTIMST; Post-doc, RGCB Thiruvananthapuram', 'department': 'Biosciences'},
        {'name': 'Dr. Sritha Sandon', 'title': 'Associate Professor', 'qualification': 'Ph.D. Educational Psychology, Martin Luther Christian University', 'department': 'Arts'},
        {'name': 'Dr. Sanjukta Mukherjee', 'title': 'Associate Professor', 'qualification': 'Ph.D., CSIR-IICB Kolkata; Post-doc, Osaka University, Japan', 'department': 'Biosciences'},
        {'name': 'Dr. Priyanka Dwivedi', 'title': 'Associate Professor of Sociology & Gender Studies', 'qualification': 'Ph.D., Bangalore University', 'department': 'Arts'},
        {'name': 'Dr. Bharath Setturu', 'title': 'Associate Professor of Computer Science', 'qualification': 'Ph.D., IIIT Hyderabad; Post-doc, IISc Bengaluru', 'department': 'Engineering'},
        {'name': 'Dr. Rajashree K', 'title': 'Associate Professor', 'qualification': 'Ph.D., LL.M., BA, LL.B., KSET', 'department': 'Law'},
        {'name': 'Sudeshna Mukherjee', 'title': 'Associate Professor, Director Social Impact Centre', 'qualification': 'Ph.D. Sociology, JNU; Public Policy, IIM Kolkata', 'department': 'Arts'},
        
        # Assistant Professors (continued from previous batch + new ones)
        {'name': 'Capt. Chaitanya Ramesh', 'title': 'Assistant Professor', 'qualification': 'M.Phil., Periyar University', 'department': 'Mathematics'},
        {'name': 'Dr. Charu Ratna Dubey', 'title': 'Assistant Professor of International Relations', 'qualification': 'Ph.D., JNU, New Delhi', 'department': 'Arts'},
        {'name': 'Sri Naresh Dixit P. S.', 'title': 'Assistant Professor, Convener IIC', 'qualification': 'M.Tech., VTU, Belagavi', 'department': 'Engineering'},
        {'name': 'Dr. Priyadarshan Kinatukara', 'title': 'Assistant Professor', 'qualification': 'Ph.D., CSIR-CCMB', 'department': 'Biosciences'},
        {'name': 'Dr. Saurav Sarmah', 'title': 'Assistant Professor of International Relations', 'qualification': 'Ph.D., JNU, New Delhi', 'department': 'Arts'},
        {'name': 'Sri Ajay Chandra', 'title': 'Assistant Professor of Psychology', 'qualification': 'M.Sc., Bangalore University', 'department': 'Arts'},
        {'name': 'Kum. Anusha M. Virupannavar', 'title': 'Assistant Professor of Environmental & Constitutional Law', 'qualification': 'LL.M., Karnataka State Law University', 'department': 'Law'},
        {'name': 'Dr. Shilpee Jain', 'title': 'Assistant Professor', 'qualification': 'Ph.D., IIT Kanpur', 'department': 'Biosciences'},
        {'name': 'Sri Praphulla Chandra N.', 'title': 'Assistant Professor of Commerce', 'qualification': 'M.Com., M.B.A., Annamalai University', 'department': 'Management'},
        {'name': 'Dr. Madhuri Mukhopadhyay', 'title': 'Assistant Professor', 'qualification': 'Ph.D., IACS, Kolkata', 'department': 'Mathematics'},
        {'name': 'Dr. Sirshendu Ghosh', 'title': 'Assistant Professor', 'qualification': 'Ph.D. Materials Chemistry, IACS Kolkata', 'department': 'Mathematics'},
        {'name': 'Dr. Vijay V.', 'title': 'Assistant Professor', 'qualification': 'Ph.D., IIT Madras', 'department': 'Engineering'},
        {'name': 'Dr. Deepthi Hebbale', 'title': 'Assistant Professor', 'qualification': 'Ph.D., IISc, Bengaluru', 'department': 'Biosciences'},
        {'name': 'Dr. Ashish Kumar Shukla', 'title': 'Assistant Professor', 'qualification': 'Ph.D., IIITDM, Jabalpur', 'department': 'Engineering'},
        {'name': 'Sri Hemanth N. V.', 'title': 'Assistant Professor of Physical Education', 'qualification': 'M.P.Ed., Mangalore University', 'department': 'Sports'},
        {'name': 'Sowmya G. S.', 'title': 'Assistant Professor, Program Lead B.Com', 'qualification': 'Ph.D., Tumkur University; Inter-ICWAI; MBA; UGC NET', 'department': 'Management'},
        {'name': 'Kum. Ambika Bhat K S', 'title': 'Assistant Professor', 'qualification': 'LL.M.', 'department': 'Law'},
        {'name': 'Dr. Kumaraswamy T R', 'title': 'Assistant Professor', 'qualification': 'Ph.D., Bangalore University', 'department': 'Arts'},
        {'name': 'Kum. Shreaya K. H.', 'title': 'Assistant Professor of Physical Education', 'qualification': 'M.P.Ed., Mangalore University', 'department': 'Sports'},
        {'name': 'Sri Giridarshan M.', 'title': 'Assistant Professor of Economics', 'qualification': 'M.A., University of Mysore', 'department': 'Arts'},
        {'name': 'Sri Deepak Raj Pandaya', 'title': 'Assistant Professor', 'qualification': 'M.A., JNU, New Delhi', 'department': 'Arts'},
        {'name': 'Dr. Mahesh Krishna K.', 'title': 'Assistant Professor', 'qualification': 'Ph.D., NIT Karnataka; Post-doc, ISI Bengaluru', 'department': 'Mathematics'},
        {'name': 'Kum. P. Susmitha', 'title': 'Assistant Professor', 'qualification': 'LL.M., Azim Premji University', 'department': 'Law'},
        {'name': 'Dr. Sindhu D. M.', 'title': 'Assistant Professor', 'qualification': 'Ph.D., Central University of Karnataka', 'department': 'Arts'},
        {'name': 'Sri Arpit', 'title': 'Assistant Professor', 'qualification': 'LL.M. (Hons.)', 'department': 'Law'},
        {'name': 'Sri Shreehari H. S.', 'title': 'Assistant Professor', 'qualification': 'M.S., Bremen University, Germany', 'department': 'Engineering'},
        {'name': 'Shubhashri Gopalkrishna Kamalapur', 'title': 'Assistant Professor', 'qualification': 'M.S.W., KSET', 'department': 'Arts'},
        {'name': 'Banashankari Hosur', 'title': 'Assistant Professor', 'qualification': 'M.Tech, RVCE, Bengaluru', 'department': 'Engineering'},
        {'name': 'Hariprasad Manjunath Hegde', 'title': 'Assistant Professor', 'qualification': 'Ph.D. Computational Science, IISc; M.Tech IISc; B.E. PESIT', 'department': 'Mathematics'},
        {'name': 'Banu Priya M.', 'title': 'Assistant Professor', 'qualification': 'M.Tech', 'department': 'Engineering'},
    ]
    
    # Get department mapping
    dept_map = {}
    for dept in Department.query.all():
        for keyword in ['Engineering', 'Management', 'Law', 'Biosciences', 'Mathematics', 'Arts']:
            if keyword in dept.name:
                dept_map[keyword] = dept.id
                break
    
    # Add special departments
    dept_map['Administration'] = dept_map.get('Arts', 1)
    dept_map['Student Affairs'] = dept_map.get('Arts', 1)
    dept_map['Academics'] = dept_map.get('Arts', 1)
    dept_map['Evaluation'] = dept_map.get('Arts', 1)
    dept_map['Sports'] = dept_map.get('Arts', 1)
    
    added = 0
    updated = 0
    skipped = 0
    
    for fac in all_faculty:
        # Create username
        username = fac['name'].lower()
        for prefix in ['prof. ', 'dr. ', 'sri ', 'kum. ', 'capt. ']:
            username = username.replace(prefix, '')
        username = username.replace(' ', '_').replace('.', '')
        
        # Check if exists
        existing = User.query.filter_by(username=username).first()
        
        # Get department ID
        dept_id = dept_map.get(fac['department'], 1)
        
        if existing:
            # Update existing user with more details
            if existing.full_name != fac['name']:
                existing.full_name = fac['name']
                updated += 1
                print(f"  Updated: {fac['name']}")
            else:
                skipped += 1
        else:
            # Create new user
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
            added += 1
            print(f"  Added: {fac['name']} - {fac['title']}")
    
    db.session.commit()
    
    print("\n" + "="*70)
    print(f"Faculty Database Update Complete!")
    print(f"  New faculty added: {added}")
    print(f"  Existing updated: {updated}")
    print(f"  Already in database: {skipped}")
    print(f"  Total faculty in database: {User.query.filter_by(role='faculty').count()}")
    print("="*70)
    
    print("\nChatbot can now answer:")
    print("  - 'Tell me about Prof. Sandeep Nair'")
    print("  - 'Who is Dr. Bharath Setturu?'")
    print("  - 'List all faculty in Engineering'")
    print("  - 'Show me faculty in Biosciences'")
