# 🎓 StudyPulse — Full-Stack Student Task & Deadline Manager

A full-stack student task and deadline management web application built with **Python Flask**, **SQLite**, and **Vanilla HTML5, CSS3, and JavaScript**.

---

## 🔗 Repository

- **GitHub Repository**: [https://github.com/kaushikbuilds-cloud/inten](https://github.com/kaushikbuilds-cloud/inten)

---

## 🎯 Project Overview

StudyPulse is designed to help students track coursework, homework assignments, and upcoming deadlines in a focused, distraction-free interface. Every registered student begins with a clean workspace (zero dummy data) and can organize their own tasks by subject, priority, and due dates.

---

## ✨ Implemented Features

### 1. 🔐 User Authentication & Session Security
- User registration (username, email, password validation).
- Password security using Werkzeug's salted password hashing (`generate_password_hash` / `check_password_hash`).
- Session-based authentication with `@login_required` decorators protecting all dashboard and API routes.
- Safe logout and session clearance.

### 2. 📋 Task & Assignment Management (CRUD)
- **Add Tasks**: Form dialog supporting Title, Subject/Course, Priority (Low, Medium, High 🔥), Due Date, and Description/Notes.
- **Mark as Completed**: Direct checkbox toggle on each task card that immediately switches status between *Pending* and *Completed* via asynchronous Fetch API requests without a page reload.
- **Edit Tasks**: Modal dialog allowing students to edit title, subject, priority, due date, description, or status.
- **Delete Tasks**: Interactive confirmation dialog preventing accidental task deletion.

### 3. ⏰ Due Dates & Overdue Status
- Computes human-friendly relative due dates: *"Due today"*, *"Due tomorrow"*, *"In 3 days"*, or *"X days overdue"*.
- Tasks that are past their due date and still pending are highlighted with a distinct danger badge and pulsating indicator.

### 4. 📊 Study Analytics
- **Total Tasks**: Total count of all enrolled tasks.
- **Pending Tasks**: Count of tasks currently in progress.
- **Completed Tasks**: Count of finished tasks.
- **Overdue Tasks**: Count of pending tasks past their due date.
- **Completion Progress (%)**: Calculated directly as `(Completed Tasks / Total Tasks) × 100` and visualized with an animated progress bar.

### 5. 🔍 Search & Multi-Criteria Filtering
- **Live Search**: Debounced search input filtering across task titles, subjects, and descriptions in real time.
- **Status Tabs**: Instant tab switching between *All*, *Pending*, *Completed*, and *Overdue*.
- **Subject Filter**: Dropdown dynamically populated with subjects from the student's active tasks.
- **Priority Filter**: Filter by High, Medium, or Low priority.
- **Sorting**: Sort by earliest due date, latest due date, priority (High to Low), or recently created.

### 6. 🎨 User Interface & Aesthetics
- Modern dark-themed workspace with custom design tokens.
- Glassmorphic top navigation bar with date display and active session indicators.
- Context-aware empty states guiding the user when no tasks exist or when search filters return 0 matches.
- Floating toast notifications providing instant feedback on user actions.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.12, Flask 3.1, Werkzeug 3.1
- **Database**: SQLite3 (with foreign keys, cascading deletes, and indexed columns)
- **Frontend**: Semantic HTML5, Vanilla CSS3 (custom dark theme, CSS variables, responsive flexbox/grid), Vanilla JavaScript (Async Fetch API)

---

## 📁 Repository Structure

```
inten/
├── app.py              # Main Flask app, routes, REST API endpoints
├── auth.py             # Authentication blueprint (registration, login, logout, session guards)
├── database.py         # SQLite connection manager and schema initialization
├── schema.sql          # Database schema (users and tasks tables, indices)
├── requirements.txt    # Python package dependencies
├── .gitignore          # Excludes virtual environments, caches, and local databases
├── README.md           # Project documentation and setup guide
├── test_app.py         # Automated unit and integration test suite
├── verify_e2e.py       # Live HTTP end-to-end test script
├── templates/
│   ├── base.html       # Shared layout with navigation and toast containers
│   ├── login.html      # Dark-themed login page
│   ├── register.html   # Dark-themed registration page
│   └── dashboard.html  # Main task manager dashboard, analytics, filters, and modals
└── static/
    ├── css/
    │   └── style.css   # Custom CSS design system, responsive rules, and animations
    └── js/
        └── app.js      # Client async logic for CRUD, status toggling, and filtering
```

---

## 🚀 How to Run Locally

### 1. Clone the Repository
```bash
git clone https://github.com/kaushikbuilds-cloud/inten.git
cd inten
```

### 2. Set Up Virtual Environment
On Windows:
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

On macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Start the Application
```bash
python app.py
```

### 5. Open in Browser
Visit **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.

---

## 🧪 Automated Testing

Run the unit and integration tests:
```bash
python test_app.py
```

Run the live HTTP end-to-end verification script:
```bash
python verify_e2e.py
```
