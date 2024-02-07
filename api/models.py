import datetime
import math

from django.contrib.auth.models import User
from django.db import models


class Marketplace(models.Model):
    id = models.AutoField(primary_key=True)


class Collection(models.Model):
    user = models.OneToOneField(
        User, related_name="collection", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=120)
    shared = models.BooleanField(default=False)
    threshold = models.IntegerField(default=75)
    start_date = models.DateField()
    end_date = models.DateField()


class Course(models.Model):
    name = models.CharField(max_length=120)
    collection = models.ForeignKey(
        Collection, related_name="courses", on_delete=models.CASCADE
    )

    def percentage(self):
        present_count = self.sessions.filter(
            status="present", date__lte=datetime.date.today()
        ).count()
        bunked_count = self.sessions.filter(status="bunked").count()
        if present_count == 0:
            return 0
        else:
            return round(present_count / (present_count + bunked_count) * 100)

    def bunks_available(self):
        total_sessions = self.sessions.count()
        must_attend = math.ceil((total_sessions * self.collection.threshold) / 100)
        total_bunks_available = total_sessions - must_attend
        bunked_sessions = self.sessions.filter(status="bunked").count()

        return total_bunks_available - bunked_sessions


class Session(models.Model):
    status_choices = models.TextChoices("StatusChoices", "present bunked cancelled")
    course = models.ForeignKey(
        Course, related_name="sessions", on_delete=models.CASCADE
    )
    date = models.DateField()
    status = models.TextField(choices=status_choices)

    # Choice fields are validated through model validation but django
    # doesnt enforce model validation on creation of new objects,
    # so we overwrite save to add validation functionality
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Schedule(models.Model):
    class day_of_week_choices(models.IntegerChoices):
        MONDAY = 1, "monday"
        TUESDAY = 2, "tuesday"
        WEDNESDAY = 3, "wednesday"
        THURSDAY = 4, "thursday"
        FRIDAY = 5, "friday"

    # day_of_week_choices = models.IntegerChoices(
    #     "DayOfWeekChoices", "monday tuesday wednesday thursday friday"
    # )
    course = models.ForeignKey(
        Course, related_name="schedules", on_delete=models.CASCADE
    )
    day_of_week = models.IntegerField(choices=day_of_week_choices)
    order = models.IntegerField(default=1)
