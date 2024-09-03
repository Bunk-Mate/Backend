#!/bin/sh
echo "Running Migrations"
python manage.py migrate

echo "Starting Server"
python manage.py runserver 0.0.0.0:8000
