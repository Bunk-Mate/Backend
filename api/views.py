import datetime
from collections import defaultdict

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import F, Max
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from api.models import Collection, Course, Schedule, Session
from api.serializers import (
    CollectionSerializer,
    CourseListSerializer,
    CourseSerializer,
    DateQuerySerializer,
    ScheduleSerializer,
    SessionSerializer,
    StatQuerySerializer,
    UserSerializer,
)
from attendence_tracker.celery import create_sessions_schedule


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "pk"


class UserRegister(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserLogin(APIView):
    def post(self, request, format=None):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            try:
                token = Token.objects.create(user=user)
            except IntegrityError:
                return Response(
                    {"User is already logged in"}, status=status.HTTP_403_FORBIDDEN
                )
            return Response({"token": token.key}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(
                {"Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )


class UserLogout(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        try:
            request.user.auth_token.delete()
        except Token.DoesNotExist:
            return Response(
                {"Token does not exist"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"Successfully logged out"}, status=status.HTTP_200_OK)


class CollectionView(generics.RetrieveUpdateDestroyAPIView, generics.CreateAPIView):
    permissions = [permissions.IsAuthenticated]
    serializer_class = CollectionSerializer
    queryset = Collection.objects.all()

    def get_object(self):
        obj = get_object_or_404(Collection, user=self.request.user)
        return obj

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

    def get(self, request):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        schedules = Schedule.objects.filter(course__collection__user=request.user)
        max_order = schedules.aggregate(Max("order", default=1))["order__max"]
        courses = []
        for order in range(1, max_order + 1):
            schedules_order = schedules.filter(order=order).values_list(
                "course__name", flat=True
            )
            courses.append(list(schedules_order))
        result = dict(serializer.data)
        result["courses"] = courses

        return Response(result, status=status.HTTP_200_OK)


class CourseListView(generics.CreateAPIView):
    permissions = [permissions.IsAuthenticated]
    serializer_class = CourseListSerializer

    def get(self, request):
        result = []
        courses = Course.objects.filter(collection__user=self.request.user)
        for course in courses:
            result.append(
                {
                    "name": course.name,
                    "schedules_url": reverse(
                        "course_schedules-list",
                        kwargs={"course_id": course.id},
                        request=request,
                    ),
                }
            )
        return Response(result, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        collection = get_object_or_404(Collection, user=self.request.user)
        serializer.save(collection=collection)


class ScheduleCreateView(generics.ListCreateAPIView):
    permissions = [permissions.IsAuthenticated]
    serializer_class = ScheduleSerializer
    lookup_field = "course_id"

    def get_queryset(self):
        id = self.kwargs.get("course_id")
        course = get_object_or_404(Course, id=id, collection__user=self.request.user)
        return Schedule.objects.filter(course=course)

    def perform_create(self, serializer):
        id = self.kwargs.get("course_id")
        course = get_object_or_404(Course, id=id)
        schedule = serializer.save(course=course)
        create_sessions_schedule.delay(
            schedule.id, course.collection.start_date, course.collection.end_date
        )


class ScheduleView(generics.RetrieveDestroyAPIView):
    permissions = [permissions.IsAuthenticated]
    serializer_class = ScheduleSerializer

    def get_queryset(self):
        return Schedule.objects.filter(course__collection__user=self.request.user.id)


class ScheduleListView(APIView):
    permissions = [permissions.IsAuthenticated]

    def get(self, request):
        schedules = Schedule.objects.filter(
            course__collection__user=request.user
        ).order_by(F("day_of_week"))
        result = defaultdict(list)
        for schedule in schedules:
            result[schedule.get_day_of_week_display()].append(
                {
                    "url": reverse(
                        "schedule-detail",
                        kwargs={"pk": schedule.id},
                        request=request,
                    ),
                    "name": schedule.course.name,
                }
            )
        return Response(result, status=status.HTTP_200_OK)


class ScheduleSelector(generics.CreateAPIView):
    permissions = [permissions.IsAuthenticated]
    serializer_class = ScheduleSerializer

    def perform_create(self, serializer):
        day = serializer.validated_data.get("day_of_week")
        schedules = Schedule.objects.filter(
            day_of_week=day, course__collection__user=self.request.user
        )
        today = datetime.date.today()
        for schedule in schedules:
            Session.objects.create(course=schedule.course, date=today, status="present")


class SessionView(generics.RetrieveUpdateDestroyAPIView):
    permissions = [permissions.IsAuthenticated]
    serializer_class = SessionSerializer

    def get_queryset(self):
        return Session.objects.filter(course__collection__user=self.request.user)


class DateQuery(APIView):
    permissions = [permissions.IsAuthenticated]

    def get(self, request):
        date_str = request.GET.get("date")
        date = datetime.date.fromisoformat(date_str)

        courses = Course.objects.filter(
            sessions__date=date, collection__user=self.request.user
        )
        # Add session status to each course
        courses = courses.annotate(status=F("sessions__status"))
        # Add session id to each course, used for building url
        courses = courses.annotate(s_id=F("sessions__id"))

        serializer = DateQuerySerializer(
            courses, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class StatQuery(generics.ListAPIView):
    permissions = [permissions.IsAuthenticated]
    serializer_class = StatQuerySerializer

    def get_queryset(self):
        return Course.objects.filter(collection__user=self.request.user)
