from collections import defaultdict

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.serializers import ValidationError

from api.models import Collection, Course, Schedule, Session
from attendence_tracker.celery import create_sessions, create_sessions_schedule


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "password"]

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as exc:
            raise serializers.ValidationError(exc)
        return value

    # Called after serialization through .save()
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class SessionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Session
        fields = ["url", "date", "status"]


class ScheduleSerializer(serializers.ModelSerializer):
    day_of_week = serializers.IntegerField(write_only=True)
    day_of_week_str = serializers.CharField(
        source="get_day_of_week_display", read_only=True
    )
    date = serializers.DateField(write_only=True, required=False)
    course_name = serializers.CharField(source="course.name", read_only=True)

    class Meta:
        model = Schedule
        fields = ["day_of_week", "order", "day_of_week_str", "course_name", "date"]


class CourseSerializer(serializers.ModelSerializer):
    schedules = ScheduleSerializer(write_only=True)

    class Meta:
        model = Course
        fields = ["name", "schedules"]

    def create(self, validated_data):
        schedule = validated_data.pop("schedules")
        collection = validated_data.get("collection")

        course = Course.objects.create(**validated_data)
        schedule = course.schedules.create(**schedule)

        create_sessions_schedule.delay(
            schedule.id, collection.start_date, collection.end_date
        )
        return course


class CollectionSerializer(serializers.ModelSerializer):
    shared = serializers.BooleanField(required=False)
    courses = CourseSerializer(many=True, read_only=True)
    courses_data = serializers.ListField(write_only=True)

    class Meta:
        model = Collection
        fields = [
            "name",
            "shared",
            "start_date",
            "end_date",
            "threshold",
            "courses",
            "courses_data",
        ]

    def create(self, validated_data):
        table_data = validated_data.pop("courses_data")
        collection = Collection.objects.create(**validated_data)

        course_list = defaultdict(list)
        for order, periods in enumerate(table_data, 1):
            for day, period in enumerate(periods, 1):
                if period != "":
                    course_list[period].append((day, order))

        for course in course_list:
            created_course = collection.courses.create(name=course)
            for schedule in course_list[course]:
                created_course.schedules.create(
                    day_of_week=schedule[0], order=schedule[1]
                )

        create_sessions.delay(collection.id, collection.start_date, collection.end_date)
        return collection

    def update(self, instance, validated_data):
        table_data = validated_data.pop("courses_data")

        instance.name = validated_data.get("name", instance.name)
        instance.shared = validated_data.get("shared", instance.shared)
        instance.threshold = validated_data.get("threshold", instance.threshold)
        instance.start_date = validated_data.get("start_date", instance.start_date)
        instance.end_date = validated_data.get("end_date", instance.end_date)
        instance.save()

        # Since this is a collection level update, passing ID's would be a hassle
        # Hence we delete all existing courses and rebuild them
        instance.courses.all().delete()
        course_list = defaultdict(list)
        for order, periods in enumerate(table_data, 1):
            for day, period in enumerate(periods, 1):
                if period != "":
                    course_list[period].append((day, order))

        for course in course_list:
            created_course = instance.courses.create(name=course)
            for schedule in course_list[course]:
                created_course.schedules.create(
                    day_of_week=schedule[0], order=schedule[1]
                )

        create_sessions.delay(instance.id, instance.start_date, instance.end_date)
        return instance


class CollectionViewSerializer(serializers.ModelSerializer):
    copy_id = serializers.IntegerField(write_only=True)
    name = serializers.CharField(read_only=True)

    class Meta:
        model = Collection
        fields = ["name", "id", "copy_id"]


class DateQuerySerializer(serializers.ModelSerializer):
    class SessionHyperlink(serializers.HyperlinkedIdentityField):
        def get_url(self, obj, view_name, request, format):
            url_kwargs = {
                "pk": obj.s_id,
            }
            return reverse(view_name, kwargs=url_kwargs, request=request, format=format)

    status = serializers.CharField()
    session_url = SessionHyperlink(read_only=True, view_name="session-detail")

    class Meta:
        model = Course
        fields = ["name", "status", "session_url"]


class StatQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["name", "percentage", "bunks_available"]
