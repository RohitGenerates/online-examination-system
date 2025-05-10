python manage.py migrate auth
python manage.py migrate contenttypes
python manage.py migrate admin
python manage.py migrate sessions
python manage.py migrate exams 0001_initial
python manage.py migrate accounts 0001_initial
python manage.py migrate accounts 0002_auto_whatever  # Your dependency migration
python manage.py migrate