import logging
import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "attendence_tracker.settings")

app = Celery("attendence_tracker")
app.conf.timezone = "Asia/Kolkata"
app.conf.broker_url = "redis://localhost:6379/0"
app.conf.result_backend = "django-db"


@app.task
def create_sessions(start_date, end_date):
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
def debug():
    logging.log("log recieved")
    print("recieved debug")


app.conf.beat_schedule = {
    "create_sessions_daily": {
        "task": "attendence_tracker.celery.debug",
        "schedule": crontab(hour=0, minute=0),
    }
}
