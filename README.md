# 🎓 StudyPulse - Student Task Manager

A full-stack, responsive student academic task and deadline management web application built with **Python Flask**, **SQLite**, and modern **HTML5 / CSS3 / Vanilla JavaScript**.

---

## ✨ Features

- **🔐 Authentication & Security**:
  - Secure student sign-up and sign-in.
  - Password hashing with Werkzeug security.
  - Session-based access control with `@login_required` route guards.
  - Automatic starter academic tasks (Calculus, Data Structures, Physics, Literature) upon registration.

- **📋 Task & Assignment Management**:
  - **Create Tasks**: Title, Subject/Course, Priority (Low, Medium, High 🔥), Due Date, and Detailed Notes.
  - **Status Management**: Instant toggle between *Pending* (In Progress) and *Completed* with smooth checkbox animations.
  - **Due Dates & Deadlines**: Smart relative date badges (*"Due today"*, *"Due tomorrow"*, *"In 3 days"*, *"2 days overdue"* with visual pulsing alert indicator).
  - **Edit & Update**: Edit task details, notes, subject, priority, and status.
  - **Delete Tasks**: Confirmation modal to prevent accidental deletion.

- **📊 Live Study Analytics**:
  - Total Tasks counter.
  - In Progress (Pending) counter.
  - Completed counter.
  - Overdue deadlines alert counter.
  - Dynamic completion rate bar (% progress).

- **🔍 Multi-Dimensional Filtering & Search**:
  - Real-time debounced search by title, description, or subject.
  - Status tabs: **All**, **Pending**, **Completed**, **Overdue**.
  - Course/Subject dropdown filter (dynamically generated from student's courses).
  - Priority filter (All, High, Medium, Low).
  - Sorting (Earliest Due Date, Latest Due Date, Priority High-to-Low, Recently Added).

---

## 🛠️ Tech Stack

- **Backend**: Python 3.12, Flask 3.1, Werkzeug 3.1
- **Database**: SQLite3 (with foreign key constraints and indexed queries)
- **Frontend**: HTML5, Vanilla CSS3 (Custom design system, CSS variables, glassmorphism, responsive grid), Vanilla JavaScript (Async Fetch API)

---

## 🚀 How to Run Locally

### 1. Activate the Virtual Environment
On Windows:
```powershell
.\.venv\Scripts\activate
```

On macOS / Linux:
```bash
source .venv/bin/activate
```

### 2. Install Dependencies (Already included in `.venv`)
```bash
pip install -r requirements.txt
```

### 3. Start the Flask Server
```powershell
python app.py
```

### 4. Open in Your Browser
Visit [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser.

---

## 🧪 Running Automated Tests

Run the test suite:
```powershell
python test_app.py
python verify_e2e.py
```

---

## 📁 Project Structure

```
d:/inten/
├── app.py              # Main Flask app, routes, REST API endpoints
├── auth.py             # Authentication blueprint, registration, login/logout, session
├── database.py         # SQLite connection helpers and starter task seeding
├── schema.sql          # Database schema (users and tasks tables, indices)
├── requirements.txt    # Python package dependencies
├── test_app.py         # Automated unit & integration tests
├── verify_e2e.py       # Live HTTP end-to-end test script
├── templates/
│   ├── base.html       # Shared responsive base layout, nav, toast container
│   ├── login.html      # Modern student login page
│   ├── register.html   # Student account registration page
│   └── dashboard.html  # Main task manager workspace with stats & filters
└── static/
    ├── css/
    │   └── style.css   # Custom styling, design tokens, animations, responsive layout
    └── js/
        └── app.js      # Interactive AJAX client logic, modals, toasts, real-time search
```
