import datetime
from collections import defaultdict

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db.models import F, Max
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.authtoken.serializers import AuthTokenSerializer

from knox.views import LoginView, LogoutView

from api.models import Collection, Course, Schedule, Session
from api.serializers import (
    CollectionSerializer,
    CollectionViewSerializer,
    CourseSerializer,
    DateQuerySerializer,
    ScheduleSerializer,
    SessionSerializer,
    StatQuerySerializer,
    UserSerializer,
)
from tasks.celery import create_sessions, create_sessions_schedule


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


class UserLogin(LoginView):
    permission_classes = [permissions.AllowAny]

    def get_post_response(self, request, token, instance):
        data = self.get_post_response_data(request, token, instance)
        return Response(data, status=202)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        return super().post(request, format=None)


class UserLogout(LogoutView):
    def get_post_response(self, request):
        return Response({"bye-bye": request.user.username}, status=200)


class CollectionView(generics.RetrieveUpdateDestroyAPIView, generics.CreateAPIView):
    permissions = [permissions.IsAuthenticated]
    serializer_class = CollectionSerializer
    queryset = Collection.objects.all()

    def perform_create(self, serializer):
        # If User has a collection, delete it
        my_collection = Collection.objects.filter(user=self.request.user)
        if my_collection:
            my_collection.delete()

        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = get_object_or_404(Collection, user=self.request.user)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def get(self, request):
        instance = get_object_or_404(Collection, user=self.request.user)
        serializer = self.get_serializer(instance)

        schedules = Schedule.objects.filter(course__collection__user=request.user)
        max_order = schedules.aggregate(Max("order", default=1))["order__max"]
        # First nested list is the first period of each day, second nested list is second period of each day
        template = [[""] * 5 for i in range(max_order)]

        for day in range(0, 5):
            schedules_on_day = schedules.filter(day_of_week=day + 1).order_by("order")
            for schedule in schedules_on_day:
                template[schedule.order - 1][
                    schedule.day_of_week - 1
                ] = schedule.course.name

        result = dict(serializer.data)
        result["courses_data"] = template
        return Response(result, status=status.HTTP_200_OK)


class CourseView(generics.CreateAPIView):
    permissions = [permissions.IsAuthenticated]
    serializer_class = CourseSerializer

    def get(self, request):
        result = []

        collection = get_object_or_404(Collection, user=self.request.user)
        courses = Course.objects.filter(collection=collection)
        for course in courses:
            result.append(
                {
                    "id": course.id,
                    "name": course.name,
                    "schedules_url": reverse(
                        "course_schedules-list",
                        kwargs={"course_id": course.id},
                        request=request,
                    ),
                }
            )
        return Response(result, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        collection = get_object_or_404(Collection, user=self.request.user)
        course = serializer.save(collection=collection)
        result = dict(serializer.data)
        result["schedules_url"] = reverse(
            "course_schedules-list", kwargs={"course_id": course.id}, request=request
        )
        return Response(result, status=status.HTTP_201_CREATED)


class ScheduleCreateView(generics.ListCreateAPIView):
    permissions = [permissions.IsAuthenticated]
    serializer_class = ScheduleSerializer
    lookup_field = "course_id"

    def get_queryset(self):
        id = self.kwargs.get("course_id")
        collection = get_object_or_404(Collection, user=self.request.user)
        course = get_object_or_404(Course, id=id, collection=collection)
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
        collection = get_object_or_404(Collection, user=self.request.user)
        return Schedule.objects.filter(course__collection=collection)


class ScheduleListView(APIView):
    permissions = [permissions.IsAuthenticated]

    def get(self, request):
        collection = get_object_or_404(Collection, user=self.request.user)
        schedules = Schedule.objects.filter(course__collection=collection).order_by(
            F("day_of_week")
        )
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
        date = serializer.validated_data.get("date")
        collection = get_object_or_404(Collection, user=self.request.user)
        schedules = Schedule.objects.filter(
            day_of_week=day, course__collection=collection
        )
        for schedule in schedules:
            Session.objects.create(course=schedule.course, date=date, status="present")


class SessionView(generics.RetrieveUpdateDestroyAPIView, generics.CreateAPIView):
    permissions = [permissions.IsAuthenticated]
    serializer_class = SessionSerializer

    def get_queryset(self):
        collection = get_object_or_404(Collection, user=self.request.user)
        return Session.objects.filter(course__collection=collection)

    def perform_create(self, serializer):
        status = serializer.validated_data.get("status", "present")
        serializer.save(status=status)


class DateQuery(APIView):
    permissions = [permissions.IsAuthenticated]

    def get(self, request):
        date_str = request.GET.get("date")
        date = datetime.date.fromisoformat(date_str)
        collection = get_object_or_404(Collection, user=self.request.user)

        courses = Course.objects.filter(sessions__date=date, collection=collection)
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
        collection = get_object_or_404(Collection, user=self.request.user)
        return Course.objects.filter(collection=collection)


class CollectionList(generics.ListAPIView):
    permissions = [permissions.IsAuthenticated]
    serializer_class = CollectionViewSerializer

    def get_queryset(self):
        return Collection.objects.filter(shared=True)


class CollectionSelector(generics.CreateAPIView):
    permissions = [permissions.IsAuthenticated]
    serializer_class = CollectionViewSerializer

    def perform_create(self, serializer):
        copy_id = serializer.validated_data.pop("copy_id")
        collection = get_object_or_404(Collection, id=copy_id)

        # If User has a collection, delete it
        my_collection = Collection.objects.filter(user=self.request.user)
        if my_collection:
            my_collection.delete()

        cloned_collection = collection.make_clone(
            attrs={"shared": False, "user": self.request.user}
        )
        create_sessions.delay(
            cloned_collection.id,
            cloned_collection.start_date,
            cloned_collection.end_date,
        )
