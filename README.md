# 🎓 AI-Powered University Assistant — Smart Campus Monitoring System

> A full-stack intelligent university management platform featuring face-recognition attendance, internal marks, student feedback, faculty dashboards, visitor management, and an AI counsellor chatbot.

---

## ✨ Features

| Module | Description |
|--------|-------------|
| **Face Recognition Attendance** | Auto-mark attendance from live camera feed |
| **Faculty Dashboard** | Marks upload, student feedback view, class HUD |
| **Student Portal** | View marks, submit feedback, events |
| **Admin Dashboard** | User management, marks config, feedback reports |
| **Security / Visitor Entry** | Entry-exit log with face verification |
| **AI Chatbot** | Gemini-powered campus assistant |
| **Counsellor Portal** | Student welfare & anonymous messages |

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/smart-campus.git
cd smart-campus
```

### 2. Create & activate virtual environment
```bash
python3 -m venv myenv
source myenv/bin/activate        # Mac/Linux
myenv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env and fill in your GOOGLE_API_KEY and SECRET_KEY
```

### 5. Initialise the database
```bash
python -c "from app import create_app; from models import db; app = create_app(); app.app_context().push(); db.create_all()"
```

### 6. (Optional) Seed sample data
```bash
python seed_faculty_subjects.py   # Seed BCA subjects for all faculty
python seed_student_courses.py    # Enrol students in their program subjects
```

### 7. Run the server
```bash
bash run.sh          # or: python app.py
```
App runs at **http://localhost:5001**

---

## 🔑 Environment Variables

Copy `.env.example` to `.env` and fill in:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Flask session secret — use a long random string |
| `GOOGLE_API_KEY` | Google Gemini API key from [makersuite.google.com](https://makersuite.google.com/app/apikey) |
| `DATABASE_URL` | SQLite (default) or PostgreSQL connection string |

> ⚠️ **Never commit `.env`** — it is listed in `.gitignore`

---

## 🗂️ Project Structure

```
├── app.py                  # Flask app factory & blueprint registration
├── models/                 # SQLAlchemy ORM models
├── routes/                 # Blueprint routes (admin, faculty, student, …)
├── templates/              # Jinja2 HTML templates
├── static/                 # CSS, JS, images
├── services/               # Face recognition, AI, visitor services
├── utils/                  # Decorators, helpers
├── .env.example            # Environment template
└── requirements.txt        # Python dependencies
```

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11 · Flask · SQLAlchemy · Flask-Login
- **AI**: Google Gemini (Generative AI) · face_recognition · OpenCV
- **Frontend**: Jinja2 · Vanilla CSS (CSS Grid) · Bootstrap icons
- **Database**: SQLite (dev) · PostgreSQL (prod-ready)

---

## 📄 License

MIT © Government Science College Hassan
