import datetime
from collections import defaultdict

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from api.models import Collection, Course, Schedule, Session
from api.serializers import (
    CollectionSerializer,
    DateQuerySerializer,
    ScheduleCreateSerializer,
    ScheduleSerializer,
    SessionSerializer,
    StatQuerySerializer,
    UserSerializer,
)


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

    # Disallow partial updates, see comment in serializers@76
    def patch(self, request, *args, **kwargs):
        return Response(
            {"detail": 'Method "PATCH" not allowed'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


class SessionView(generics.RetrieveDestroyAPIView):
    permissions = [permissions.IsAuthenticated]
    serializer_class = SessionSerializer

    def get_queryset(self):
        return Session.objects.filter(course__collection__user=self.request.user)


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

    def post(self, request):
        serializer = ScheduleCreateSerializer(data=self.request.data)
        if serializer.is_valid():
            day_of_week = serializer.validated_data.get("day_of_week")
            course_name = serializer.validated_data.get("course_name")
            collection = get_object_or_404(Collection, user=request.user)
            course = Course.objects.create(name=course_name, collection=collection)
            Schedule.objects.create(course=course, day_of_week=day_of_week)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_200_OK)


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
