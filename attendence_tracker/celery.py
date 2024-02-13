import logging
import os

from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

if "WEBSITE_HOSTNAME" in os.environ:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "attendence_tracker.production")
    broker_url = os.getenv("AZURE_REDIS_BROKER_CONNECTIONSTRING")
else:
    load_dotenv("./.creds")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "attendence_tracker.settings")
    broker_url = os.getenv("BROKERLOCATION")

import django

django.setup()

app = Celery("attendence_tracker")
app.conf.timezone = "Asia/Kolkata"
app.conf.broker_url = broker_url
app.conf.result_backend = "django-db"


@app.task
def create_sessions(start_date, end_date):
    """Create sessions for all schedules"""
    from api.dateutils import working_days
    from api.models import Schedule, Session

    schedules = Schedule.objects.all()
    session_objs = []
    for day in working_days(start_date, end_date):
        for schedule in schedules:
            if (
                schedule.day_of_week - 1
            ) == day.weekday():  # python weekday starts at 0
                session_objs.append(
                    Session(date=day, course=schedule.course, status="present")
                )
                logging.info(
                    f"added session for {schedule.course.name} on date {day.strftime('%Y-%m-%d')}"
                )

    Session.objects.bulk_create(session_objs)
    return f"Inserted {len(session_objs)} sessions into the database"


@app.task
def create_sessions_schedule(schedule_id, start_date, end_date):
    """Create sessions for one schedule"""
    from api.dateutils import working_days
    from api.models import Schedule, Session

    schedule = Schedule.objects.get(id=schedule_id)

    session_objs = []
    for day in working_days(start_date, end_date):
        if (schedule.day_of_week - 1) == day.weekday():
            session_objs.append(
                Session(date=day, course=schedule.course, status="present")
            )
            logging.info(
                f"added session for {schedule.course.name} on date {day.strftime('%Y-%m-%d')}"
            )

    Session.objects.bulk_create(session_objs)
    return f"Inserted {len(session_objs)} sessions into the database"


@app.task
def debug():
    logging.log("log recieved")
    print("recieved debug")
