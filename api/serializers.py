from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.serializers import ValidationError


class UserSerializer(serializers.ModelSerializer):
    # books = serializers.PrimaryKeyRelatedField(
    #     required=False, many=True, queryset=Book.objects.all()
    # )
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
