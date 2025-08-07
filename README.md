# Online Examination System

A robust, secure, and feature-rich online examination platform built with Python and Django.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.x-darkgreen?logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-blue?logo=postgresql&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Table of Contents

- [Project Overview](#project-overview)
- [Live Demo & Screenshots](#live-demo--screenshots)
- [Core Features](#core-features)
- [Technology Stack](#technology-stack)
- [System Architecture & Database Schema](#system-architecture--database-schema)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Key Learnings & Technical Challenges](#key-learnings--technical-challenges)
- [Contributing](#contributing)
- [License](#license)

---

## Project Overview

The Online Examination System is a comprehensive web application designed to modernize academic assessments. It provides educational institutions with a secure, efficient, and user-friendly platform for creating exams, conducting tests, and managing results. The system streamlines the entire examination lifecycle, from question creation by teachers to real-time exam-taking by students and automated grading, all while upholding academic integrity.

This project was developed as a group project for a Database Management Systems course, demonstrating a strong understanding of database design, web development, and software engineering principles.

### Key Objectives
- To provide a secure and reliable platform for conducting online examinations.
- To empower teachers with tools for efficient exam and question bank management.
- To offer students a seamless and fair exam-taking experience with features like real-time timers.
- To automate the grading process and provide insightful result analysis.
- To ensure academic integrity through robust security and monitoring features.

---

## Live Demo & Screenshots

**(Recommended)** A live demo or a series of screenshots/GIFs can dramatically increase a recruiter's engagement.

* **[Link to Live Demo]** (If deployed)
* **Screenshots:**
    * *Student Dashboard & Exam View*
    * *Teacher Exam Creation Form*
    * *Admin User Management Panel*
    * *Result Analysis Page*

---

## Core Features

### 👤 User Roles & Permissions
The system supports three distinct user roles with tailored dashboards and permissions.

* 👑 **Admin**
    * Complete system oversight and management.
    * Manage all user accounts (Teachers, Students).
    * Create, update, and delete academic departments.
    * Monitor system-wide activity and view comprehensive statistics.

* 🧑‍🏫 **Teacher**
    * Create, schedule, and manage exams for their departments and subjects.
    * Build and maintain a comprehensive question bank.
    * View and analyze student results for the exams they have created.
    * Publish or withhold results.
    * Manage their personal profile.

* 🧑‍🎓 **Student**
    * Register and manage their profile, including department and semester.
    * View a list of available and upcoming exams.
    * Take exams in a real-time, timed environment.
    * Submit answers and receive instant (or delayed) results.
    * View their exam history and performance analysis.

### ✨ Special Features
- **Secure Authentication:** Robust login system with password validation and session management.
- **Role-Based Access Control (RBAC):** Granular permissions ensuring users can only access authorized functionalities.
- **Real-time Exam Timer:** A client-side timer synchronized with the server to enforce time limits.
- **Data Validation:** Strict input validation on all forms to maintain data integrity.
- **CSRF Protection:** Built-in Django security to prevent cross-site request forgery.
- **Result Publishing Control:** Teachers have the authority to decide when to release exam results to students.

---

## Technology Stack

| Category | Technology |
| :--- | :--- |
| **Backend** | Python, Django Framework |
| **Frontend** | HTML, CSS, JavaScript |
| **Database** | PostgreSQL |
| **Deployment**| Django Development Server, Gunicorn/Nginx (Production Ready) |
| **VCS** | Git & GitHub |

---

## System Architecture & Database Schema

The system is built on a normalized relational database schema designed for scalability and data integrity.

### Main Tables
`User` (Custom), `Student`, `Teacher`, `Department`, `Subject`, `Question`, `Exam`, `ExamAttempt`, `StudentExamResult`

### Key Relationships
- A `User` has a one-to-one relationship with either a `Student` or a `Teacher`. This allows for a unified authentication system while separating role-specific data.
- An `Exam` belongs to one `Department` and one `Subject`.
- An `Exam` is composed of many `Questions` ($ \text{Many-to-Many relationship} $).
- An `ExamAttempt` represents a student's single attempt at an `Exam`.
- A `StudentExamResult` links a `Student` to their final score on an `Exam`.

### Constraints
- Primary Keys defined for all tables.
- Foreign Key relationships are established with `ON DELETE CASCADE` or `ON DELETE SET NULL` where appropriate to maintain referential integrity.
- `UNIQUE` constraints on usernames, email addresses, and department codes.
- `UNIQUE TOGETHER` constraints to prevent a student from attempting the same exam multiple times.

---

## Getting Started

Follow these instructions to set up the project locally for development and testing.

### Prerequisites
- Python (3.8+)
- PostgreSQL
- Git

### Installation & Setup
1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd online-examination-system
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure your database** in `exam_system/settings.py`.

5.  **Run database migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Create an administrative superuser:**
    ```bash
    python manage.py createsuperuser
    ```

7.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The application will be available at `http://127.0.0.1:8000`.

---

## Project Structure

exam_system/
├── accounts/            # App for user management, authentication, and profiles
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
├── exams/               # App for exam/question creation and result management
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
├── templates/           # Global base templates with navigation and footer
├── static/              # Global static files (CSS, JS, images)
└── exam_system/         # Main Django project configuration
    ├── settings.py
    ├── urls.py
    └── wsgi.py

---

## Key Learnings & Technical Challenges

This project provided invaluable hands-on experience and presented several technical challenges that were successfully overcome:

1.  **Advanced Authentication & Authorization:**
    * **Challenge:** Implementing a secure authentication system that could handle different user roles (Admin, Teacher, Student) with distinct permissions.
    * **Solution:** Developed a custom Django User model and leveraged Django's built-in authentication system. Implemented role-based access control using decorators and middleware to protect routes and functionalities, ensuring a secure and segregated user experience.

2.  **Dynamic Frontend with Django Templates:**
    * **Challenge:** Integrating a static HTML/CSS frontend with the Django backend, making it dynamic and data-driven.
    * **Solution:** Mastered the Django Templating Language (DTL), including template inheritance, context processors, and custom template tags. This allowed for the creation of reusable UI components and a clean separation of logic and presentation.

3.  **Complex Database Relationships:**
    * **Challenge:** Designing an efficient and normalized database schema, particularly for handling the many-to-many relationship between exams and questions.
    * **Solution:** Designed the schema using ER modeling principles. Implemented the `ManyToManyField` in Django to create the association table between `Exam` and `Question`. Utilized database cascading rules to ensure data integrity during deletion operations.

4.  **Real-time Functionality with JavaScript:**
    * **Challenge:** Implementing a real-time exam timer and handling asynchronous form submissions without full page reloads.
    * **Solution:** Utilized JavaScript to create a countdown timer for the exam interface. For future enhancements, developed a plan to integrate the AJAX/Fetch API to submit answers and update the UI asynchronously, improving user experience.

---

## Contributing

Contributions are welcome! If you'd like to improve the system, please follow these steps:

1.  Fork the repository.
2.  Create a new feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.