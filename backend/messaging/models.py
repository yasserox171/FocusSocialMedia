from django.conf import settings
from django.db import models


class Conversation(models.Model):
    """
    Strictly 1-to-1 conversation. user_a always holds the lower user id so
    each pair maps to exactly one conversation row.
    """

    user_a = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conversations_a"
    )
    user_b = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conversations_b"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user_a", "user_b")
        ordering = ["-updated_at"]

    @classmethod
    def between(cls, u1, u2):
        a, b = sorted([u1, u2], key=lambda u: u.id)
        conv, _ = cls.objects.get_or_create(user_a=a, user_b=b)
        return conv

    def includes(self, user):
        return user.id in (self.user_a_id, self.user_b_id)

    def other(self, user):
        return self.user_b if user.id == self.user_a_id else self.user_a


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="messages_sent"
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]
