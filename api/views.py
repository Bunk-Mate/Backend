from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import (
    AttendanceSerializer,
    CollectionSerializer,
    CourseSerializer,
    ScheduleSerializer,
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


class CollectionView(generics.ListCreateAPIView):
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

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    # Disallow partial updates, see comment in serializers@77
    def patch(self, request, *args, **kwargs):
        return Response(
            {"detail": "Patch method is not allowed"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
