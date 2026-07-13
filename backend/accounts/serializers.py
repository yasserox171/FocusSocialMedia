from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Invite, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "display_name", "bio", "avatar", "kind",
                  "is_active", "date_joined"]
        read_only_fields = ["id", "username", "kind", "is_active", "date_joined"]


class AdminUserSerializer(serializers.ModelSerializer):
    """Full user management from the admin dashboard."""

    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ["id", "username", "display_name", "bio", "avatar", "kind",
                  "is_active", "is_staff", "date_joined", "password"]
        read_only_fields = ["id", "date_joined"]

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save(update_fields=["password"])
        return user


class InviteSerializer(serializers.ModelSerializer):
    used = serializers.BooleanField(source="is_used", read_only=True)

    class Meta:
        model = Invite
        fields = ["id", "token", "display_name", "note", "created_at", "used"]
        read_only_fields = ["id", "token", "created_at", "used"]


class InviteAcceptSerializer(serializers.Serializer):
    token = serializers.CharField()
    username = serializers.CharField(max_length=150)
    password = serializers.CharField()

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("اسم المستخدم مأخوذ.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value
