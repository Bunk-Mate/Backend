from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from api.models import Collection, Course, Schedule, Session


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


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ["date", "status"]


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ["day_of_week"]


class CourseSerializer(serializers.ModelSerializer):
    schedules = ScheduleSerializer(many=True)

    class Meta:
        model = Course
        fields = ["name", "schedules"]


class CollectionSerializer(serializers.ModelSerializer):
    shared = serializers.BooleanField(required=False)
    courses = CourseSerializer(many=True)

    class Meta:
        model = Collection
        fields = ["name", "shared", "courses"]

    def create(self, validated_data):
        courses_data = validated_data.pop("courses")
        user = validated_data.pop("user")
        collection = user.collections.create(**validated_data)

        for course_data in courses_data:
            schedules_data = course_data.pop("schedules")
            course = collection.courses.create(**course_data)
            for schedule_data in schedules_data:
                course.schedules.create(**schedule_data)

        return collection

    def update(self, instance, validated_data):
        courses_data = validated_data.pop("courses")

        instance.name = validated_data.get("name", instance.name)
        instance.shared = validated_data.get("shared", instance.shared)
        instance.save()

        # Since this is a collection level update, passing ID's would be a hassle
        # Hence we delete all existing courses and rebuild them
        instance.courses.all().delete()
        for course_data in courses_data:
            schedules_data = course_data.pop("schedules")
            course = instance.courses.create(**course_data)
            for schedule_data in schedules_data:
                course.schedules.create(**schedule_data)

        return instance
