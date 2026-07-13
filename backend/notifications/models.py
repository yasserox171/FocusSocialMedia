from django.conf import settings
from django.db import models


class Notification(models.Model):
    """
    Stored notification, also pushed live over the /ws/notifications/ socket.
    kind: like | message | new_post
    """

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications_sent",
        null=True,
    )
    kind = models.CharField(max_length=20)
    text = models.CharField(max_length=300)
    post_id = models.BigIntegerField(null=True, blank=True)
    conversation_id = models.BigIntegerField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
