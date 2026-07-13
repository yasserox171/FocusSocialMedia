from rest_framework import serializers

from accounts.serializers import UserSerializer

from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "conversation", "sender", "text", "created_at", "is_read"]
        read_only_fields = ["id", "conversation", "sender", "created_at", "is_read"]


class ConversationSerializer(serializers.ModelSerializer):
    other_user = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Conversation
        fields = ["id", "other_user", "last_message", "unread_count", "updated_at"]

    def get_other_user(self, obj):
        user = self.context["request"].user
        return UserSerializer(obj.other(user), context=self.context).data

    def get_last_message(self, obj):
        last = obj.messages.last()
        return MessageSerializer(last).data if last else None
