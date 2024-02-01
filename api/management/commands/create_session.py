import calendar
import datetime

from django.core.management.base import BaseCommand, CommandError

from api.models import Course, Schedule, Session


class Command(BaseCommand):
    help = "Create daily sessions based on the schedule"

    def handle(self, *args, **options):
        date = datetime.date.today()
        day_str = calendar.day_name[date.weekday()].lower()

        schedules = Schedule.objects.filter(day_of_week=day_str)
        for schedule in schedules:
            course = schedule.course
            existing_session = Session.objects.filter(course=course, date=date)
            Session.objects.create(course=course, date=date, status="present")
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created session for {date} for course {course.name} in {course.collection.name}"
                )
            )
