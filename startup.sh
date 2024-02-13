export LANG=C.UTF-8
gunicorn --bind=0.0.0.0 --timeout 600 attendence_tracker.wsgi & celery -A attendence_tracker worker -l info
