# Online Examination System

A comprehensive online examination system built with Django that allows teachers to create and manage exams, and students to take exams and view their results.

## Features

- User authentication and authorization (Students, Teachers, Admins)
- Exam creation and management
- Question randomization
- Real-time exam taking with timer
- Automatic grading
- Detailed result analysis and statistics
- Responsive design

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd exam_system
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Usage

### Students
- Register as a student with department and semester information
- View available exams
- Take exams within the specified time limit
- View exam results and performance analysis

### Teachers
- Register as a teacher with department information
- Create and manage exams
- Add questions with multiple choice options
- View exam results and student performance
- Generate detailed statistics and reports

### Admins
- Manage user accounts
- Monitor system activity
- View comprehensive statistics

## Project Structure

```
exam_system/
├── accounts/           # User management app
│   ├── models.py      # User models
│   ├── views.py       # User views
│   ├── urls.py        # User URLs
│   └── templates/     # User templates
├── exams/             # Exam management app
│   ├── models.py      # Exam models
│   ├── views.py       # Exam views
│   ├── urls.py        # Exam URLs
│   └── templates/     # Exam templates
├── templates/         # Base templates
├── static/            # Static files
└── exam_system/       # Project settings
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 