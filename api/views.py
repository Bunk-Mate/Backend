import datetime

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Count, F
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Course, Session
from api.serializers import (
    CollectionSerializer,
    CourseSerializer,
    DateQuerySerializer,
    ScheduleSerializer,
    SessionSerializer,
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


class CollectionListView(generics.ListCreateAPIView):
    permissions = [permissions.IsAuthenticated]
    serializer_class = CollectionSerializer

    def get_queryset(self):
        return self.request.user.collections.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CollectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    permissions = [permissions.IsAuthenticated]
    serializer_class = CollectionSerializer

    def get_queryset(self):
        return self.request.user.collections.all()

    # Disallow partial updates, see comment in serializers@77
    def patch(self, request, *args, **kwargs):
        return Response(
            {"detail": 'Method "PATCH" not allowed'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


class SessionDetailView(generics.RetrieveUpdateAPIView):
    permissions = [permissions.IsAuthenticated]
    serializer_class = SessionSerializer

    def get_queryset(self):
        return Session.objects.filter(course__collection__user=self.request.user)


class DateQuery(APIView):
    permissions = [permissions.IsAuthenticated]

    def get(self, request):
        date_str = request.GET.get("date")
        date = datetime.date.fromisoformat(date_str)
        courses = Course.objects.filter(sessions__date=date)
        # Add session status to each course
        courses = courses.annotate(status=F("sessions__status"))
        # Add session id to each course, used for building url
        courses = courses.annotate(s_id=F("sessions__id"))

        serializer = DateQuerySerializer(
            courses, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
