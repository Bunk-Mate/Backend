from django.contrib.auth.models import User
from django.db import models


class Marketplace(models.Model):
    id = models.AutoField(primary_key=True)


class Collection(models.Model):
    user = models.ForeignKey(User, related_name="collections", on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    shared = models.BooleanField(default=False)


class Course(models.Model):
    name = models.CharField(max_length=120)
    collection = models.ForeignKey(
        Collection, related_name="courses", on_delete=models.CASCADE
    )

    @property
    def percentage(self):
        if self.attended == 0:
            return 0
        return round(self.attended / (self.attended + self.missed), 2)


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
    day_of_week_choices = models.TextChoices(
        "DayOfWeekChoices", "monday tuesday wednesday thursday friday"
    )
    course = models.ForeignKey(
        Course, related_name="schedules", on_delete=models.CASCADE
    )
    day_of_week = models.TextField(choices=day_of_week_choices)
