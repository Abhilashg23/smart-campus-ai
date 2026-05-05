import requests
import json
from flask import current_app
from models import db, Event, Department, User, ChatHistory
from models.student_tracking import StudentTracking
from datetime import datetime, timedelta
import pytz


# Faculty and Staff Location Database
FACULTY_LOCATIONS = {
    # Academic Block 1 - 4th Floor
    'shrinivas s. balli': {'name': 'Prof. Shrinivas S. Balli', 'role': 'Dean Student Affairs', 'cabin': '425', 'floor': '4th Floor', 'building': 'Academic Block 1'},
    'shrinivas balli': {'name': 'Prof. Shrinivas S. Balli', 'role': 'Dean Student Affairs', 'cabin': '425', 'floor': '4th Floor', 'building': 'Academic Block 1'},
    'balli': {'name': 'Prof. Shrinivas S. Balli', 'role': 'Dean Student Affairs', 'cabin': '425', 'floor': '4th Floor', 'building': 'Academic Block 1'},
    
    'chetan basavaraj singai': {'name': 'Prof. Chetan Basavaraj Singai', 'role': 'Dean School of Law, Governance and Public Policy', 'cabin': '426', 'floor': '4th Floor', 'building': 'Academic Block 1'},
    'chetan singai': {'name': 'Prof. Chetan Basavaraj Singai', 'role': 'Dean School of Law, Governance and Public Policy', 'cabin': '426', 'floor': '4th Floor', 'building': 'Academic Block 1'},
    'singai': {'name': 'Prof. Chetan Basavaraj Singai', 'role': 'Dean School of Law, Governance and Public Policy', 'cabin': '426', 'floor': '4th Floor', 'building': 'Academic Block 1'},
    
    'dinesh shenoy': {'name': 'Dr. Dinesh Shenoy', 'role': 'Dean School of Management Science', 'cabin': '427', 'floor': '4th Floor', 'building': 'Academic Block 1'},
    'shenoy': {'name': 'Dr. Dinesh Shenoy', 'role': 'Dean School of Management Science', 'cabin': '427', 'floor': '4th Floor', 'building': 'Academic Block 1'},
    
    'sandeep nair': {'name': 'Prof. Sandeep Nair', 'role': 'Dean School of Arts, Humanities and Social Sciences', 'cabin': '428', 'floor': '4th Floor', 'building': 'Academic Block 1'},
    'nair': {'name': 'Prof. Sandeep Nair', 'role': 'Dean School of Arts, Humanities and Social Sciences', 'cabin': '428', 'floor': '4th Floor', 'building': 'Academic Block 1'},
    
    'yashavantha dongre': {'name': 'Prof. Yashavantha Dongre', 'role': 'Vice Chancellor', 'cabin': '464 & 466', 'floor': '4th Floor', 'building': 'Academic Block 1'},
    'dongre': {'name': 'Prof. Yashavantha Dongre', 'role': 'Vice Chancellor', 'cabin': '464 & 466', 'floor': '4th Floor', 'building': 'Academic Block 1'},
    'vice chancellor': {'name': 'Prof. Yashavantha Dongre', 'role': 'Vice Chancellor', 'cabin': '464 & 466', 'floor': '4th Floor', 'building': 'Academic Block 1'},
    'vc': {'name': 'Prof. Yashavantha Dongre', 'role': 'Vice Chancellor', 'cabin': '464 & 466', 'floor': '4th Floor', 'building': 'Academic Block 1'},
    
    's. somanath': {'name': 'Dr. S. Somanath', 'role': 'Chancellor', 'cabin': '465', 'floor': '4th Floor', 'building': 'Academic Block 1'},
    'somanath': {'name': 'Dr. S. Somanath', 'role': 'Chancellor', 'cabin': '465', 'floor': '4th Floor', 'building': 'Academic Block 1'},
    'chancellor': {'name': 'Dr. S. Somanath', 'role': 'Chancellor', 'cabin': '465', 'floor': '4th Floor', 'building': 'Academic Block 1'},
    
    # Academic Block 1 - 3rd Floor
    'bhavani m. r': {'name': 'Dr. Bhavani M. R', 'role': 'Office of Registrar (Evaluation)', 'cabin': '358', 'floor': '3rd Floor', 'building': 'Academic Block 1'},
    'bhavani': {'name': 'Dr. Bhavani M. R', 'role': 'Office of Registrar (Evaluation)', 'cabin': '358', 'floor': '3rd Floor', 'building': 'Academic Block 1'},
    
    'registrar office': {'name': 'Registrar Office', 'role': '', 'cabin': '351', 'floor': '3rd Floor', 'building': 'Academic Block 1'},
    'registrar': {'name': 'Registrar Office', 'role': '', 'cabin': '351', 'floor': '3rd Floor', 'building': 'Academic Block 1'},
    
    'finance office': {'name': 'Finance Office', 'role': '', 'cabin': '377 & 378', 'floor': '3rd Floor', 'building': 'Academic Block 1'},
    'finance': {'name': 'Finance Office', 'role': '', 'cabin': '377 & 378', 'floor': '3rd Floor', 'building': 'Academic Block 1'},
    
    'human resource section': {'name': 'Human Resource Section', 'role': '', 'cabin': '345', 'floor': '3rd Floor', 'building': 'Academic Block 1'},
    'hr section': {'name': 'Human Resource Section', 'role': '', 'cabin': '345', 'floor': '3rd Floor', 'building': 'Academic Block 1'},
    'hr': {'name': 'Human Resource Section', 'role': '', 'cabin': '345', 'floor': '3rd Floor', 'building': 'Academic Block 1'},
    
    # Academic Block 1 - 1st Floor
    'admin front office': {'name': 'Admin Front Office', 'role': '', 'cabin': '139', 'floor': '1st Floor', 'building': 'Academic Block 1'},
    'admin meeting room': {'name': 'Admin Meeting Room', 'role': '', 'cabin': '140', 'floor': '1st Floor', 'building': 'Academic Block 1'},
    'admission hall': {'name': 'Admission Hall', 'role': '', 'cabin': '167', 'floor': '1st Floor', 'building': 'Academic Block 1'},
    'admissions': {'name': 'Admission Hall', 'role': '', 'cabin': '167', 'floor': '1st Floor', 'building': 'Academic Block 1'},
    'hostel warden': {'name': 'Hostel Warden', 'role': '', 'cabin': '136', 'floor': '1st Floor', 'building': 'Academic Block 1'},
    'digi campus verification': {'name': 'Digi Campus Verification', 'role': '', 'cabin': '171', 'floor': '1st Floor', 'building': 'Academic Block 1'},
    
    # Academic Block 1 - Ground Floor
    'library': {'name': 'Library', 'role': '', 'cabin': 'U42', 'floor': 'Ground Floor', 'building': 'Academic Block 1'},
    
    'bharathkumar v': {'name': 'Bharathkumar V', 'role': 'Library Incharge', 'cabin': 'U46', 'floor': 'Ground Floor', 'building': 'Academic Block 1'},
    'bharathkumar': {'name': 'Bharathkumar V', 'role': 'Library Incharge', 'cabin': 'U46', 'floor': 'Ground Floor', 'building': 'Academic Block 1'},
    'library incharge': {'name': 'Bharathkumar V', 'role': 'Library Incharge', 'cabin': 'U46', 'floor': 'Ground Floor', 'building': 'Academic Block 1'},
    
    'library adviser': {'name': 'Library Adviser', 'role': '', 'cabin': 'U45', 'floor': 'Ground Floor', 'building': 'Academic Block 1'},
    'library office': {'name': 'Library Office & Repro', 'role': '', 'cabin': 'U43', 'floor': 'Ground Floor', 'building': 'Academic Block 1'},
    
    # Academic Block 2 - A Wing
    'bharath setturu': {'name': 'Dr. Bharath Setturu', 'role': '', 'cabin': '1', 'floor': 'Floor 1', 'building': 'Academic Block 2 A Wing'},
    'setturu': {'name': 'Dr. Bharath Setturu', 'role': '', 'cabin': '1', 'floor': 'Floor 1', 'building': 'Academic Block 2 A Wing'},
    
    'rajesh kumar prasad': {'name': 'Dr. Rajesh Kumar Prasad', 'role': '', 'cabin': '2', 'floor': 'Floor 1', 'building': 'Academic Block 2 A Wing'},
    'rajesh prasad': {'name': 'Dr. Rajesh Kumar Prasad', 'role': '', 'cabin': '2', 'floor': 'Floor 1', 'building': 'Academic Block 2 A Wing'},
    
    'deepak b': {'name': 'Deepak B', 'role': '', 'cabin': '3', 'floor': 'Floor 1', 'building': 'Academic Block 2 A Wing'},
    'deepak': {'name': 'Deepak B', 'role': '', 'cabin': '3', 'floor': 'Floor 1', 'building': 'Academic Block 2 A Wing'},
    
    'ashith sagar naidu': {'name': 'Ashith Sagar Naidu', 'role': '', 'cabin': '3', 'floor': 'Floor 1', 'building': 'Academic Block 2 A Wing'},
    'ashith': {'name': 'Ashith Sagar Naidu', 'role': '', 'cabin': '3', 'floor': 'Floor 1', 'building': 'Academic Block 2 A Wing'},
    
    'gannavaram sridhar': {'name': 'Gannavaram Sridhar', 'role': '', 'cabin': '3', 'floor': 'Floor 1', 'building': 'Academic Block 2 A Wing'},
    'sridhar': {'name': 'Gannavaram Sridhar', 'role': '', 'cabin': '3', 'floor': 'Floor 1', 'building': 'Academic Block 2 A Wing'},
    
    'bhuvana yv': {'name': 'Bhuvana YV', 'role': '', 'cabin': '3', 'floor': 'Floor 1', 'building': 'Academic Block 2 A Wing'},
    
    'pradeep kumar gopalakrishnan': {'name': 'Sri Pradeep Kumar Gopalakrishnan', 'role': '', 'cabin': '4', 'floor': 'Floor 1', 'building': 'Academic Block 2 A Wing'},
    'pradeep kumar': {'name': 'Sri Pradeep Kumar Gopalakrishnan', 'role': '', 'cabin': '4', 'floor': 'Floor 1', 'building': 'Academic Block 2 A Wing'},
    
    'upkar singh': {'name': 'Dr. Upkar Singh', 'role': '', 'cabin': 'CU7', 'floor': 'Floor 1', 'building': 'Academic Block 2 A Wing'},
    
    'arun kumar': {'name': 'Dr. Arun Kumar', 'role': '', 'cabin': 'CU5', 'floor': 'Floor 1', 'building': 'Academic Block 2 A Wing'},
    
    'chitra gp': {'name': 'Chitra GP', 'role': '', 'cabin': 'CU1', 'floor': 'Floor 1', 'building': 'Academic Block 2 A Wing'},
    'chitra': {'name': 'Chitra GP', 'role': '', 'cabin': 'CU1', 'floor': 'Floor 1', 'building': 'Academic Block 2 A Wing'},
    
    'banu priya m': {'name': 'Banu Priya M', 'role': '', 'cabin': 'CU6', 'floor': 'Floor 1', 'building': 'Academic Block 2 A Wing'},
    'banu priya': {'name': 'Banu Priya M', 'role': '', 'cabin': 'CU6', 'floor': 'Floor 1', 'building': 'Academic Block 2 A Wing'},
    
    'bhagirathi t': {'name': 'Bhagirathi T', 'role': '', 'cabin': 'CU3', 'floor': 'Floor 1', 'building': 'Academic Block 2 A Wing'},
    'bhagirathi': {'name': 'Bhagirathi T', 'role': '', 'cabin': 'CU3', 'floor': 'Floor 1', 'building': 'Academic Block 2 A Wing'},
    
    'bhavana m': {'name': 'Bhavana M', 'role': '', 'cabin': 'CU4', 'floor': 'Floor 1', 'building': 'Academic Block 2 A Wing'},
    
    'mulla arshiya': {'name': 'Mulla Arshiya', 'role': '', 'cabin': 'CU2', 'floor': 'Floor 1', 'building': 'Academic Block 2 A Wing'},
    'arshiya': {'name': 'Mulla Arshiya', 'role': '', 'cabin': 'CU2', 'floor': 'Floor 1', 'building': 'Academic Block 2 A Wing'},
    
    # Academic Block 2 - B Wing
    'shobana': {'name': 'Shobana', 'role': '', 'cabin': '1', 'floor': 'Floor 1', 'building': 'Academic Block 2 B Wing'},
    
    'ashish kumar': {'name': 'Ashish Kumar', 'role': '', 'cabin': '2', 'floor': 'Floor 1', 'building': 'Academic Block 2 B Wing'},
    'ashish': {'name': 'Ashish Kumar', 'role': '', 'cabin': '2', 'floor': 'Floor 1', 'building': 'Academic Block 2 B Wing'},
    
    'vijay': {'name': 'Vijay', 'role': '', 'cabin': '3', 'floor': 'Floor 1', 'building': 'Academic Block 2 B Wing'},
    
    'naresh': {'name': 'Naresh', 'role': '', 'cabin': '4', 'floor': 'Floor 1', 'building': 'Academic Block 2 B Wing'},
    
    'nithesh': {'name': 'Nithesh', 'role': '', 'cabin': 'CU1', 'floor': 'Floor 1', 'building': 'Academic Block 2 B Wing'},
    
    'bhanashankari hosur': {'name': 'Bhanashankari Hosur', 'role': '', 'cabin': 'CU2', 'floor': 'Floor 1', 'building': 'Academic Block 2 B Wing'},
    'bhanashankari': {'name': 'Bhanashankari Hosur', 'role': '', 'cabin': 'CU2', 'floor': 'Floor 1', 'building': 'Academic Block 2 B Wing'},
    
    'nikhil': {'name': 'Nikhil', 'role': '', 'cabin': 'CU3', 'floor': 'Floor 1', 'building': 'Academic Block 2 B Wing'},
    
    'sathyamanikanta': {'name': 'Sathyamanikanta', 'role': '', 'cabin': 'CU4', 'floor': 'Floor 1', 'building': 'Academic Block 2 B Wing'},
    
    'dharaneesh': {'name': 'Dharaneesh', 'role': '', 'cabin': 'CU5', 'floor': 'Floor 1', 'building': 'Academic Block 2 B Wing'},
    
    'amogh': {'name': 'Amogh', 'role': '', 'cabin': 'CU6', 'floor': 'Floor 1', 'building': 'Academic Block 2 B Wing'},
}



class ChatbotService:
    """AI Chatbot service using Google Generative AI"""
    
    def __init__(self):
        self.api_key = None
        self.model_name = 'gemini-1.5-flash'  # Use a robust stable model
        self.last_response_image = None  # Store image URL for person queries
    
    def initialize(self, api_key):
        """Initialize the Gemini service via REST API"""
        if api_key:
            self.api_key = api_key
            print(f"Chatbot initialized using REST API with model {self.model_name}")
        else:
            print("Warning: Google API key not configured. Chatbot will not work.")
    
    def get_context_data(self):
        """Get context data about campus for better responses"""
        context = {
            'events': [],
            'departments': []
        }
        
        # Get upcoming events
        upcoming_events = Event.query.filter(
            Event.event_date >= datetime.utcnow()
        ).order_by(Event.event_date.asc()).limit(10).all()
        
        for event in upcoming_events:
            context['events'].append({
                'title': event.title,
                'description': event.description,
                'date': event.event_date.strftime('%Y-%m-%d %H:%M'),
                'location': event.location
            })
        
        # Get departments
        departments = Department.query.all()
        for dept in departments:
            context['departments'].append({
                'name': dept.name,
                'head': dept.head_of_department,
                'email': dept.contact_email,
                'phone': dept.contact_phone
            })
            
        # Get faculty and staff
        context['faculty'] = []
        staff_members = User.query.filter(User.role.in_(['faculty', 'Faculty', 'staff', 'Staff'])).all()
        for fac in staff_members:
            context['faculty'].append({
                'name': fac.full_name,
                'designation': fac.designation or fac.role,
                'subjects': fac.specialization or '',
                'cabin': fac.bio or ''
            })
        
        return context
    
    def get_faculty_info(self, faculty_name):
        """Get detailed faculty information with availability status"""
        # Search for faculty by name (case-insensitive, partial match)
        faculty = User.query.filter(
            User.role.in_(['faculty', 'Faculty']),
            User.full_name.ilike(f'%{faculty_name}%')
        ).first()
        
        if not faculty:
            return None
        
        # Get availability status
        ist = pytz.timezone('Asia/Kolkata')
        today_start = datetime.now(ist).replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        tracking_records = StudentTracking.query.filter(
            StudentTracking.user_id == faculty.id,
            StudentTracking.timestamp >= today_start,
            StudentTracking.timestamp < today_end
        ).order_by(StudentTracking.timestamp.desc()).all()
        
        availability_status = "Not entered today"
        last_entry_time = None
        
        if tracking_records:
            last_record = tracking_records[0]
            last_entry_time = last_record.timestamp.astimezone(ist).strftime('%I:%M %p')
            
            if last_record.entry_type == 'IN':
                availability_status = f"Currently in university (entered at {last_entry_time})"
            else:
                availability_status = f"Left university (last exit at {last_entry_time})"
        
        return {
            'name': faculty.full_name,
            'email': faculty.email,
            'designation': faculty.designation or 'Faculty Member',
            'department': faculty.department.name if faculty.department else 'Not assigned',
            'education': faculty.education or 'Not available',
            'bio': faculty.bio or 'No biography available',
            'research_interests': faculty.research_interests or 'Not specified',
            'profile_image': faculty.profile_image or faculty.profile_picture,
            'availability': availability_status
        }
    
    def build_prompt(self, user_message, user_role=None):
        """Build context-aware prompt"""
        context = self.get_context_data()
        
        system_context = f"""You are a helpful AI assistant for Government Science College ( Autonomous ) Hassan campus. 
You have access to the following information:



GOVERNMENT SCIENCE (AUTONOMOUS) HASSAN INFORMATION:

ABOUT THE COLLEGE:
Government Science College (Autonomous), Hassan is a premier government science college affiliated to Hassan University. The college has been educating students of the district in science streams for over six decades. The University Grants Commission (UGC) – New Delhi conferred autonomous status to the college from the year 2015-16. The college is accredited with NAAC B with CGPA 2.13. Website: https://gfgc.karnataka.gov.in/hassan_science/public/en

LEADERSHIP:
- Principal: Dr. PRASANNA K S (Associate Professor in Zoology)

PROGRAMMES OFFERED:
- MSc Chemistry (MSc-Chem) – CBCS
- BSc Physics & Mathematics (PM)
- BSc Physics & Chemistry (PC)
- BSc Physics & Computer Science (PCs)
- BSc Physics & Electronics (PE)
- BSc Mathematics & Computer Science (MCs)
- BSc Mathematics & Electronics (ME)
- BSc Mathematics & Chemistry (MC)
- BSc Electronics & Computer Science (ECs)
- BSc Botany & Zoology (BZ)
- BSc Botany & Chemistry (BC)
- BSc Zoology & Chemistry (ZC)
- BSc Biotechnology & Chemistry (BtC)
- BSc Botany & Biochemistry (BBc)
- BSc Zoology & Biotechnology (ZBt)
- BSc Microbiology & Biotechnology (MbBt)
- BSc Biotechnology & Biochemistry (BtBC)
- BSc Microbiology & Biochemistry (MbBc)
- BSc Microbiology & Botany (MbB)
- BSc Biochemistry & Zoology (BCZ)
- BSc Biotechnology & Botany (BBT)
- BSc Zoology & Microbiology (ZMB)
- BCA (NEP-2020)

ADMISSIONS:
- Contact: gsc_hassan@rediffmail.com
- Website: https://gfgc.karnataka.gov.in/hassan_science/public/en
- Location: Hassan, Karnataka – 573201
- Affiliation: Hassan University
- UGC Autonomous status from 2015-16
- NAAC B with CGPA 2.13

FACILITIES:
- Well-equipped laboratories, library, virtual class, Wi-Fi campus
- INFLIBNET access, JIPC (Job Information and Placement Cell)
- Girls' hostel, canteen
- NSS, NCC, Sports, Cultural activities
- Samvedana Balaga (free mid-day meal program for needy students)
- Certificate courses offered by each department
- PG program: MSc Chemistry

QUALITY INITIATIVES:
- IQAC (Internal Quality Assurance Cell)
- NAAC B accreditation (CGPA 2.13)
- Green Campus initiatives
- Best Practices
"""
        
        
        if context['events']:
            for event in context['events']:
                system_context += f"- {event['title']}: {event['description']} on {event['date']} at {event['location']}\n"
        else:
            system_context += "No upcoming events scheduled.\n"
        
        system_context += "\nDEPARTMENTS:\n"
        if context['departments']:
            for dept in context['departments']:
                system_context += f"- {dept['name']}: Head - {dept['head']}, Contact: {dept['email']}, Phone: {dept['phone']}\n"
        else:
            system_context += "No department information available.\n"
            
        system_context += "\nKEY FACULTY AND STAFF:\n"
        if context.get('faculty'):
            for fac in context['faculty']:
                system_context += f"- {fac['name']} – {fac['designation']}"
                if fac.get('subjects'):
                    system_context += f", Subjects: {fac['subjects']}"
                if fac.get('cabin'):
                    system_context += f", {fac['cabin']}"
                system_context += "\n"
        else:
            system_context += "No faculty information available.\n"
        
        system_context += f"""
Please answer the user's question based on this information. Be helpful, concise, and friendly.

CRITICAL INSTRUCTIONS - READ CAREFULLY:
⚠️ ONLY provide information that is explicitly stated above
⚠️ DO NOT make up or invent faculty names, contact details, or any other information
⚠️ DO NOT hallucinate or fabricate details that are not in the provided context
⚠️ If specific information (like a dean's name or contact) is NOT listed above, say "I don't have that specific information" and suggest visiting the school office or website
⚠️ DO NOT use asterisks (*) or markdown formatting in your responses - use plain text only
⚠️ Write responses in clear, natural language without special formatting characters

GUIDELINES:
- If asked about Government Science (Autonomous) Hassan, programmes, or admissions, use ONLY the college information provided above
- If asked about locations, directions, or faculty rooms, use ONLY the faculty locations provided
- If asked about events, schedules, or departments, use ONLY the information provided
- For questions about specific programmes or courses, refer to the appropriate department
- For admissions queries, direct to: gsc_hassan@rediffmail.com or https://gfgc.karnataka.gov.in/hassan_science/public/en
- If you don't have specific information, say so clearly and suggest: "For detailed information, please visit https://gfgc.karnataka.gov.in/hassan_science/public/en or contact the college office"
- NEVER invent names, phone numbers, email addresses, or other contact details
- Use plain text without asterisks, bold, or other markdown formatting

User's role: {user_role or 'Guest'}
User's question: {user_message}
"""
        
        return system_context
    
    def get_response(self, user_message, user_id=None, user_role=None):
        """Get chatbot response using direct REST API call"""
        # Reset image URL for new query
        self.last_response_image = None
        
        # Try Gemini REST API
        if self.api_key:
            try:
                # Build context-aware prompt
                prompt_text = self.build_prompt(user_message, user_role)
                
                # API Endpoint
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
                
                # Payload
                payload = {
                    "contents": [{
                        "parts": [{"text": prompt_text}]
                    }]
                }
                
                headers = {'Content-Type': 'application/json'}
                
                # Direct HTTP call
                response = requests.post(url, headers=headers, json=payload)
                response_json = response.json()
                
                if 'candidates' in response_json and len(response_json['candidates']) > 0:
                    response_text = response_json['candidates'][0]['content']['parts'][0]['text']
                    
                    # Store in chat history if user is logged in
                    if user_id:
                        chat_record = ChatHistory(
                            user_id=user_id,
                            message=user_message,
                            response=response_text,
                            chat_type='text'
                        )
                        db.session.add(chat_record)
                        db.session.commit()
                    
                    return {
                        'response': response_text,
                        'image_url': None
                    }
                else:
                    error_msg = response_json.get('error', {}).get('message', 'Unknown API error')
                    print(f"Gemini API error: {error_msg}")
            
            except Exception as e:
                print(f"REST API wrapper error: {str(e)}")
                # Fall through to fallback
        
        # Fallback: Rule-based responses using database
        response_text = self.get_fallback_response(user_message, user_role)
        
        # Store in chat history
        if user_id:
            try:
                chat_record = ChatHistory(
                    user_id=user_id,
                    message=user_message,
                    response=response_text,
                    chat_type='text'
                )
                db.session.add(chat_record)
                db.session.commit()
            except:
                pass
        
        # Return response with image URL if available
        return {
            'response': response_text,
            'image_url': self.last_response_image
        }
    
    def check_person_availability(self, person_name):
        """Check if a specific person is currently in the university"""
        import pytz
        
        # Search for the user by name
        user = User.query.filter(
            db.or_(
                User.full_name.ilike(f'%{person_name}%'),
                User.first_name.ilike(f'%{person_name}%'),
                User.last_name.ilike(f'%{person_name}%')
            )
        ).first()
        
        if not user:
            return None, "Person not found in the system.", None
        
        # Get today's date in IST
        ist = pytz.timezone('Asia/Kolkata')
        now_ist = datetime.now(ist)
        today_ist = now_ist.date()
        
        # Get all tracking records for this user
        all_tracking_records = StudentTracking.query.filter(
            StudentTracking.user_id == user.id
        ).order_by(StudentTracking.timestamp.desc()).all()
        
        # Filter records for today in IST
        tracking_records = []
        for record in all_tracking_records:
            # Convert UTC timestamp to IST
            utc_time = record.timestamp.replace(tzinfo=pytz.UTC)
            ist_time = utc_time.astimezone(ist)
            if ist_time.date() == today_ist:
                tracking_records.append(record)
        
        # Build detailed user information
        response = f"**{user.full_name}**\n\n"
        
        # Add role
        if user.role:
            response += f"📋 Role: {user.role}\n"
        
        # Add department for students and faculty
        if user.department:
            response += f"🏛️ Department: {user.department.name}\n"
        
        # Add program for students
        if hasattr(user, 'program') and user.program:
            response += f"🎓 Program: {user.program.name}\n"
        
        # Add designation for faculty
        if user.designation:
            response += f"💼 Designation: {user.designation}\n"
        
        # Add email
        response += f"📧 Email: {user.email}\n\n"
        
        # Check presence status
        if not tracking_records:
            response += f"❌ **Status**: Has not entered the university today."
        else:
            # Check the last entry
            last_entry = tracking_records[0]
            
            # Convert entry time to IST for display
            utc_time = last_entry.timestamp.replace(tzinfo=pytz.UTC)
            ist_time = utc_time.astimezone(ist)
            
            if last_entry.entry_type == 'IN':
                # Person is currently in the university
                entry_time = ist_time.strftime('%I:%M %p')
                response += f"✅ **Status**: Currently in the university\n"
                response += f"🕐 Entered at: {entry_time} today"
            else:
                # Person has exited
                exit_time = ist_time.strftime('%I:%M %p')
                response += f"❌ **Status**: Has left the university\n"
                response += f"🕐 Last exit at: {exit_time} today"
        
        # Extract profile image URL
        image_url = None
        if user.profile_image:
            image_url = user.profile_image
        elif user.profile_picture:
            image_url = user.profile_picture
        
        return user, response, image_url
    
    def get_all_present_people(self, role=None):
        """Get all people currently present in the university"""
        import pytz
        
        # Get today's date in IST
        ist = pytz.timezone('Asia/Kolkata')
        now_ist = datetime.now(ist)
        today_ist = now_ist.date()
        
        # Get all tracking records
        query = db.session.query(User, StudentTracking).join(
            StudentTracking, User.id == StudentTracking.user_id
        )
        
        if role:
            query = query.filter(User.role == role)
        
        # Get all tracking records
        all_records = query.all()
        
        # Filter for today in IST and group by user
        user_status = {}
        for user, tracking in all_records:
            # Convert UTC timestamp to IST
            utc_time = tracking.timestamp.replace(tzinfo=pytz.UTC)
            ist_time = utc_time.astimezone(ist)
            
            # Only include records from today (IST)
            if ist_time.date() == today_ist:
                if user.id not in user_status:
                    user_status[user.id] = {'user': user, 'entries': []}
                user_status[user.id]['entries'].append(tracking)
        
        # Determine who is currently present
        present_users = []
        for user_id, data in user_status.items():
            # Sort entries by timestamp descending
            sorted_entries = sorted(data['entries'], key=lambda x: x.timestamp, reverse=True)
            # Check if last entry is IN
            if sorted_entries[0].entry_type == 'IN':
                present_users.append({
                    'user': data['user'],
                    'entry_time': sorted_entries[0].timestamp
                })
        
        return present_users
    
    def get_fallback_response(self, user_message, user_role=None):
        """Fallback rule-based chatbot using database"""
        message_lower = user_message.lower()
        
        # Check for availability queries first
        availability_keywords = [
            'available', 'present', 'in university', 'in campus', 'here today', 
            'came today', 'in college', 'on campus', 'at university', 'at college',
            'entered today', 'came in', 'checked in', 'is here', 'are here',
            'inside', 'inside university', 'inside campus', 'on site'
        ]
        is_availability_query = any(keyword in message_lower for keyword in availability_keywords)
        
        # Also check for student-specific queries
        student_query_patterns = [
            'student', 'students', 'tell me about', 'who is', 'information about',
            'info about', 'details about', 'find student'
        ]
        is_student_query = any(pattern in message_lower for pattern in student_query_patterns)
        
        if is_availability_query or is_student_query or 'is' in message_lower:
            # Check if asking about a specific person
            # Extract potential name from the query
            # Common patterns: "Is [name] available?", "Is [name] in university?", "Is [name] present today?"
            # "Tell me about student [name]", "Is student [name] present?"
            
            potential_name = None
            
            # Try to extract name after "is"
            if 'is ' in message_lower:
                # Get the part after "is"
                after_is = message_lower.split('is ', 1)[1]
                
                # Remove common phrases (order matters - remove longer phrases first)
                removal_phrases = [
                    'student ', 'faculty ', 'professor ', 'prof ', 'dr ',
                    'in the university', 'in university', 'in the campus', 'in campus',
                    'in college', 'in the college', 'on campus', 'on the campus',
                    'at university', 'at the university', 'at college', 'at the college',
                    'available', 'present', 'here today', 'here', 'today',
                    'came today', 'entered today', 'checked in', 'inside', 'the', '?', '.'
                ]
                
                for phrase in removal_phrases:
                    after_is = after_is.replace(phrase, '')
                
                # Clean up extra spaces
                potential_name = ' '.join(after_is.split())
            
            # Try to extract name after "student" or "about"
            elif 'student ' in message_lower or 'about ' in message_lower:
                # Try "student [name]" pattern
                if 'student ' in message_lower:
                    after_student = message_lower.split('student ', 1)[1]
                else:
                    after_student = message_lower.split('about ', 1)[1]
                
                # Remove common phrases
                removal_phrases = [
                    'named ', 'called ', 'is ', 'in the university', 'in university', 
                    'in the campus', 'in campus', 'present', 'available', 
                    'here', 'today', 'the', '?', '.'
                ]
                
                for phrase in removal_phrases:
                    after_student = after_student.replace(phrase, '')
                
                # Clean up extra spaces
                potential_name = ' '.join(after_student.split())
            
            # If we found a potential name, check availability
            if potential_name and len(potential_name) > 2:
                user, message, image_url = self.check_person_availability(potential_name)
                if user:
                    # Store image URL in instance variable for API to access
                    self.last_response_image = image_url
                    return message
            
            # Check for "who is present" or "list present students/faculty"
            if any(phrase in message_lower for phrase in ['who is present', 'who are present', 'list present', 'show present', 'all present']):
                role = None
                if 'student' in message_lower:
                    role = 'Student'
                elif 'faculty' in message_lower or 'teacher' in message_lower or 'professor' in message_lower:
                    role = 'Faculty'
                
                present_people = self.get_all_present_people(role)
                
                if present_people:
                    role_text = f"{role}s" if role else "People"
                    response = f"✅ {role_text} currently present in the university ({len(present_people)}):\n\n"
                    for i, person_data in enumerate(present_people[:20], 1):  # Limit to 20
                        user = person_data['user']
                        entry_time = person_data['entry_time'].strftime('%I:%M %p')
                        response += f"{i}. {user.full_name}"
                        if user.role:
                            response += f" ({user.role})"
                        response += f" - Entered at {entry_time}\n"
                    
                    if len(present_people) > 20:
                        response += f"\n... and {len(present_people) - 20} more"
                    
                    return response.strip()
                else:
                    role_text = f"{role}s" if role else "people"
                    return f"No {role_text} are currently present in the university today."
        
        # Enhanced keyword mapping for schools/departments
        school_keywords = {
            'computer_science': ['computer', 'cs', 'bca', 'programming'],
            'physics': ['physics'],
            'chemistry': ['chemistry'],
            'mathematics': ['math', 'mathematics'],
            'botany': ['botany', 'biology', 'plants'],
            'zoology': ['zoology', 'animals'],
            'languages': ['english', 'kannada', 'languages']
        }
        
        # Check for "tell me about [school]" or similar queries
        if any(phrase in message_lower for phrase in ['tell me about', 'about', 'what is', 'information about', 'info about']):
            for school_type, keywords in school_keywords.items():
                if any(keyword in message_lower for keyword in keywords):
                    # Find the department
                    dept = Department.query.filter(Department.name.like(f'%{school_type}%')).first()
                    if dept:
                        response = f"📚 {dept.name}\n\n"
                        if dept.head_of_department:
                            response += f"👤 Head: {dept.head_of_department}\n"
                        if dept.contact_email:
                            response += f"📧 Email: {dept.contact_email}\n"
                        if dept.contact_phone:
                            response += f"📞 Phone: {dept.contact_phone}\n"
                        
                        # Get faculty count
                        faculty_count = User.query.join(Department).filter(
                            User.role == 'faculty',
                            Department.id == dept.id
                        ).count()
                        
                        if faculty_count > 0:
                            response += f"\n👨‍🏫 Faculty Members: {faculty_count}\n"
                            response += f"\nWould you like to know more about our faculty? Ask me 'List Computer Science faculty' or 'Tell me about a specific professor'."
                        
                        return response
                    else:
                        # Generic response about the school
                        school_names = {
                            'computer_science': 'Department of Computer Science',
                            'physics': 'Department of Physics',
                            'chemistry': 'Department of Chemistry',
                            'mathematics': 'Department of Mathematics',
                            'botany': 'Department of Botany',
                            'zoology': 'Department of Zoology',
                            'languages': 'Department of Languages'
                        }
                        return f"The {school_names.get(school_type, 'department')} is one of our premier academic divisions. For more specific information, please contact the administration office."
        
        # Faculty queries (e.g., "Tell me about Prof. Sandeep Nair", "Who is Prof. Ashok?")
        if any(word in message_lower for word in ['prof', 'professor', 'faculty', 'dr.', 'teacher']):
            # Check if asking about a specific faculty member
            faculty_keywords = ['tell me about', 'who is', 'about', 'information']
            if any(keyword in message_lower for keyword in faculty_keywords):
                # Try to find faculty by name
                users = User.query.filter_by(role='faculty').all()
                
                for user in users:
                    # Check if faculty name is in the message
                    name_parts = user.full_name.lower().split()
                    if any(part in message_lower for part in name_parts if len(part) > 3):
                        response = f"{user.full_name}\n\n"
                        if user.designation:
                            response += f"Designation: {user.designation}\n"
                        if user.department:
                            response += f"Department: {user.department.name}\n"
                        if user.education:
                            response += f"Education: {user.education}\n"
                        if user.bio:
                            response += f"\nAbout: {user.bio}\n"
                        if user.research_interests:
                            response += f"\nResearch Interests: {user.research_interests}\n"
                        response += f"\nEmail: {user.email}"
                        
                        # Add profile image if available
                        if user.profile_image:
                            response += f"\n\nProfile Image: {user.profile_image}"
                        elif user.university_profile_url:
                            response += f"\n\nProfile: {user.university_profile_url}"
                        
                        return response
                
                # If no specific faculty found, ask for clarification
                return "I can help you find information about our faculty. Please provide the faculty member's name. For example: 'Tell me about Prof. Sandeep Nair'"
            
            # List all faculty or faculty by department
            elif 'list' in message_lower or 'all' in message_lower:
                # Check if asking for specific department
                dept_keywords = {
                    'computer': 'Computer Science',
                    'cs': 'Computer Science',
                    'bca': 'Computer Science',
                    'physics': 'Physics',
                    'chemistry': 'Chemistry',
                    'math': 'Mathematics',
                    'botany': 'Botany',
                    'zoology': 'Zoology',
                    'kannada': 'Kannada',
                    'english': 'English'
                }
                
                target_dept = None
                for keyword, dept_name in dept_keywords.items():
                    if keyword in message_lower:
                        target_dept = dept_name
                        break
                
                if target_dept:
                    # List faculty from specific department
                    faculty = User.query.join(Department).filter(
                        User.role.in_(['faculty', 'Faculty']),
                        Department.name.like(f'%{target_dept}%')
                    ).all()
                    
                    if faculty:
                        dept_full_name = faculty[0].department.name if faculty[0].department else target_dept
                        response = f"Faculty in {dept_full_name}:\n\n"
                        for i, fac in enumerate(faculty, 1):
                            response += f"{i}. {fac.full_name}\n"
                            response += f"   Email: {fac.email}\n\n"
                        return response.strip()
                    else:
                        return f"No faculty found in {target_dept} department."
                else:
                    # List all faculty (limit to 10)
                    faculty = User.query.filter(User.role.in_(['faculty', 'Faculty'])).limit(10).all()
                    if faculty:
                        response = "Faculty at Government Science College ( Autonomous ) Hassan (showing first 10):\n\n"
                        for i, fac in enumerate(faculty, 1):
                            response += f"{i}. {fac.full_name}\n"
                            if fac.department:
                                response += f"   Department: {fac.department.name}\n"
                            response += f"   Email: {fac.email}\n\n"
                        return response.strip()
        
        # Specific department head query (e.g., "Who is the head of Engineering?")
        if 'head' in message_lower and 'of' in message_lower:
            # Extract department name
            dept_keywords = {
                'computer': 'Department of Computer Science',
                'cs': 'Department of Computer Science',
                'physics': 'Department of Physics',
                'chemistry': 'Department of Chemistry',
                'math': 'Department of Mathematics',
                'botany': 'Department of Botany',
                'zoology': 'Department of Zoology',
                'kannada': 'Department of Kannada',
                'english': 'Department of English'
            }
            
            for keyword, dept_name in dept_keywords.items():
                if keyword in message_lower:
                    dept = Department.query.filter(Department.name.like(f'%{dept_name}%')).first()
                    if dept:
                        response = f"{dept.name}\n\n"
                        if dept.head_of_department:
                            response += f"Head: {dept.head_of_department}\n"
                        if dept.contact_email:
                            response += f"Email: {dept.contact_email}\n"
                        if dept.contact_phone:
                            response += f"Phone: {dept.contact_phone}"
                        return response
            
            # If no specific department found, ask for clarification
            return "I can help you find the head of a department. Which department are you interested in? (Computer Science, Physics, Chemistry, Botany, Zoology, Mathematics, Kannada, or English)"
        
        # Specific department contact query
        elif 'contact' in message_lower and any(word in message_lower for word in ['computer', 'physics', 'chemistry', 'math', 'botany', 'zoology', 'english', 'kannada']):
            dept_keywords = {
                'computer': 'Computer Science',
                'physics': 'Physics',
                'chemistry': 'Chemistry',
                'math': 'Mathematics',
                'botany': 'Botany',
                'zoology': 'Zoology',
                'english': 'English',
                'kannada': 'Kannada'
            }
            
            for keyword, search_term in dept_keywords.items():
                if keyword in message_lower:
                    dept = Department.query.filter(Department.name.like(f'%{search_term}%')).first()
                    if dept:
                        response = f"Contact Information for {dept.name}:\n\n"
                        if dept.contact_email:
                            response += f"Email: {dept.contact_email}\n"
                        if dept.contact_phone:
                            response += f"Phone: {dept.contact_phone}\n"
                        if dept.head_of_department:
                            response += f"\nHead: {dept.head_of_department}"
                        return response
        
        # Events queries
        elif any(word in message_lower for word in ['event', 'happening', 'schedule', 'upcoming']):
            upcoming_events = Event.query.filter(
                Event.event_date >= datetime.utcnow()
            ).order_by(Event.event_date.asc()).limit(5).all()
            
            if upcoming_events:
                response = "Upcoming Events at Government Science College ( Autonomous ) Hassan:\n\n"
                for i, event in enumerate(upcoming_events, 1):
                    response += f"{i}. {event.title}\n"
                    response += f"   Date: {event.event_date.strftime('%B %d, %Y at %I:%M %p')}\n"
                    response += f"   Location: {event.location}\n"
                    if event.description:
                        # Truncate long descriptions
                        desc = event.description[:150] + "..." if len(event.description) > 150 else event.description
                        response += f"   Info: {desc}\n"
                    response += "\n"
                return response.strip()
            else:
                return "There are no upcoming events scheduled at the moment. Please check back later!"
        
        # General department list query
        elif 'department' in message_lower or 'school' in message_lower:
            # Check if asking about all departments
            if any(word in message_lower for word in ['all', 'list', 'what', 'tell me about']):
                departments = Department.query.all()
                
                if departments:
                    response = "Departments at Government Science College ( Autonomous ) Hassan:\n\n"
                    for i, dept in enumerate(departments, 1):
                        response += f"{i}. {dept.name}\n"
                        if dept.head_of_department:
                            response += f"   Head: {dept.head_of_department}\n"
                        if dept.contact_email:
                            response += f"   Email: {dept.contact_email}\n"
                        response += "\n"
                    return response.strip()
                else:
                    return "Department information is not available at the moment."
            else:
                # Asking about departments in general
                return "We have several departments at Government Science College ( Autonomous ) Hassan including Physics, Chemistry, Mathematics, Botany, Zoology, and more.\n\nAsk me about a specific department to learn more!"
        
        # Location queries - Check faculty/staff locations first
        elif any(word in message_lower for word in ['where', 'location', 'find', 'located', 'cabin', 'office']):
            # Search for faculty/staff in the message
            found_location = None
            
            # Normalize the message by removing common titles and punctuation
            normalized_message = message_lower.replace('dr.', '').replace('prof.', '').replace('professor', '').replace('.', '').replace(',', '').strip()
            
            # Try to find exact matches or partial matches
            for key, location_data in FACULTY_LOCATIONS.items():
                if key in normalized_message:
                    found_location = location_data
                    break
            
            if found_location:
                # Format the response
                response = f"{found_location['name']}"
                if found_location['role']:
                    response += f" ({found_location['role']})"
                response += f" is located in:\n"
                response += f"  Cabin: {found_location['cabin']}\n"
                response += f"  Floor: {found_location['floor']}\n"
                response += f"  Building: {found_location['building']}"
                return response
            
            # If no specific faculty found, fallback to old location mapping
            locations = {
                'library': 'Upper Ground Floor, Administrative Block "A" Wing',
                'auditorium': 'Upper Ground Floor, Administrative Block "A" Wing',
                'incubation': 'Upper Ground Floor, Administrative Block "A" Wing',
                'incubation centre': 'Upper Ground Floor, Administrative Block "A" Wing',
                'vice chancellor': '4th Floor, Administrative Block "A" Wing',
                'vc': '4th Floor, Administrative Block "A" Wing',
                'dean': '4th Floor, Administrative Block "A" Wing',
                'registrar': '3rd Floor, Administrative Block "A" Wing',
                'finance': '3rd Floor, Administrative Block "A" Wing',
                'communication': '3rd Floor, Administrative Block "A" Wing',
                'procurement': '3rd Floor, Administrative Block "A" Wing',
                'store': '2nd Floor, Administrative Block "A" Wing',
                'classroom': '2nd Floor, Administrative Block "A" Wing',
                'ug classroom': '2nd Floor, Administrative Block "A" Wing',
                'coo': '1st Floor, Administrative Block "A" Wing',
                'admission': '1st Floor, Administrative Block "A" Wing',
                'administrative': '1st Floor, Administrative Block "A" Wing',
                'data centre': 'Lower Ground Floor, Administrative Block "A" Wing',
                'bms': 'Lower Ground Floor, Administrative Block "A" Wing',
                'cafeteria': 'Admin Block 1, LG B Wing',
                'canteen': 'Admin Block 1, LG B Wing'
            }
            
            # Find matching location
            for keyword, location in locations.items():
                if keyword in message_lower:
                    response = f"The {keyword.title()} is located at {location}."
                    # Add timings if available
                    if keyword == 'library':
                        response += "\n\nLibrary Timings:\n9:30 AM to 9:30 PM, Monday to Saturday"
                    elif keyword in ['cafeteria', 'canteen']:
                        response += "\n\nCafeteria Timings:\n9:00 AM to 7:30 PM, Monday to Saturday"
                    return response
            
            # If no specific location found, provide general info
            return """I can help you find faculty and staff locations on campus!

Try asking:
- "Where is Prof. Shrinivas S. Balli?"
- "Where is the library?"
- "What time does the cafeteria open?"
- "Library timings?"
- "What is Naresh's cabin number?"
- "Where is the finance office?"

Or ask me about specific faculty members, offices, or campus locations!"""
        
        # Timing queries for library and cafeteria
        elif any(word in message_lower for word in ['timing', 'timings', 'time', 'hours', 'open', 'close', 'schedule']):
            if 'library' in message_lower:
                return """Library Timings:
📚 9:30 AM to 9:30 PM
📅 Monday to Saturday
📍 Location: Upper Ground Floor, Administrative Block "A" Wing (Cabin U42)

For more information, contact:
Bharathkumar V (Library Incharge) - Cabin U46"""
            elif any(word in message_lower for word in ['cafeteria', 'canteen', 'food', 'dining']):
                return """Cafeteria Timings:
🍽️ 9:00 AM to 7:30 PM
📅 Monday to Saturday
📍 Location: Admin Block 1, LG B Wing

Enjoy your meals!"""
            else:
                return """I can help you with timings for:

📚 Library: 9:30 AM to 9:30 PM (Monday to Saturday)
🍽️ Cafeteria: 9:00 AM to 7:30 PM (Monday to Saturday)

What would you like to know more about?"""
        
        # Help/greeting
        elif any(word in message_lower for word in ['hello', 'hi', 'hey', 'help', 'what can you']):
            return """Hello! I'm your Government Science College ( Autonomous ) Hassan AI assistant. I can help you with:

- Student/Faculty Info - "Who is Geetha C D?" or "Is Darshan S J present?"
- Presence Status - "Is [student name] in the college today?"
- Locations - "Where is the Library?"
- Events - "What events are coming up?"
- Departments - "Tell me about Computer Science"
- Contact - "Who is the Principal?"

What would you like to know?"""
        
        # Thanks
        elif any(word in message_lower for word in ['thank', 'thanks']):
            return "You're welcome! Feel free to ask if you need anything else."
        
        # Default response - ask for clarification
        else:
            return """I didn't quite understand that. Could you please rephrase your question?

I can help you with:

- Student/Faculty Info - "Who is [name]?" or "Is [name] present?"
- Campus locations - "Where is the Library?"
- Upcoming events - "What events are happening?"
- Department information - "Tell me about Computer Science"
- Faculty information - "List Computer Science faculty"
- Contact details - "Who is the Principal?"

What would you like to know?"""


# Global chatbot instance
chatbot = ChatbotService()
