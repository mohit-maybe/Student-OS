# 🎓 Student OS - University Management Portal

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

> A premium, secure, and modern university management system built with Flask.

## 🌟 Overview
**Student OS** is a comprehensive web application designed to streamline academic operations. It features a beautiful glassmorphism UI, role-based access control (Student, Teacher, Admin), and secure data handling.

## ✨ Key Features
- **🔐 Secure Authentication:** Role-based login with hashed passwords and session management.
- **🛡️ Enterprise Security:** Complete CSRF protection on all forms and secure environment variable management.
- **🎨 Premium UI/UX:** Responsive design with glassmorphism, dark mode support, and smooth animations.
- **🌍 Internationalization:** Multi-language support for global accessibility.
- **📊 Academic Management:**
    - **Admissions:** Enroll students and auto-generate credentials.
    - **Grading:** Teachers can record grades and generate reports.
    - **Attendance:** Daily tracking with visual indicators.
- **💬 Communication:** Built-in messaging system between users.

## 🛠️ Tech Stack
- **Backend:** Python, Flask, Flask-Login, Flask-WTF, Flask-Mail
- **Database:** SQLite (Development) / PostgreSQL (Production ready)
- **Frontend:** Jinja2 Templates, Vanilla CSS (Glassmorphism design), JavaScript
- **Security:** CSRF Protection, Dotenv Secret Management

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Git

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/student-os.git
    cd student-os
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment**
    Create a `.env` file in the root directory:
    ```env
    SECRET_KEY='your-super-secret-key'
    MAIL_USERNAME='your-email@gmail.com'
    MAIL_PASSWORD='your-app-password'
    ```

5.  **Initialize Database**
    The application will automatically create the database on the first run if it doesn't exist.

6.  **Run the Application**
    ```bash
    python app.py
    ```
    Visit `http://localhost:5000` in your browser.

## 👤 Credentials (Demo)
- **Admin:** `admin` / `admin123`
- **Teacher:** Create via Admin portal
- **Student:** Enrolled via Teacher portal

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
