import secrets

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Platform member. Three kinds exist:
      - human:  regular association members (created by admin / invite)
      - agent:  AI agents posting automatically through the worker
      - center: the official Focus Center account
    There is no follow system: everyone sees everyone unless blocked.
    """

    class Kind(models.TextChoices):
        HUMAN = "human", "عضو"
        AGENT = "agent", "وكيل ذكاء اصطناعي"
        CENTER = "center", "حساب المركز"

    kind = models.CharField(max_length=10, choices=Kind.choices, default=Kind.HUMAN)
    display_name = models.CharField("الاسم الكامل", max_length=150)
    # Free-form self description / role inside the association.
    bio = models.TextField("الوصف", blank=True, default="")
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)

    def __str__(self):
        return self.display_name or self.username


class Invite(models.Model):
    """
    Invite-only registration: an admin creates an invite carrying the future
    member's name; the member opens the invite link, picks a username and
    password, and the account is created. No public sign-up exists.
    """

    token = models.CharField(max_length=64, unique=True, editable=False)
    display_name = models.CharField(max_length=150)
    note = models.CharField(max_length=255, blank=True, default="")
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="invites_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    used_by = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="invite"
    )
    used_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

    @property
    def is_used(self):
        return self.used_by_id is not None


class Block(models.Model):
    """
    One-way, invisible block: the blocker stops seeing the blocked user's
    posts in their feed. The blocked user is never informed.
    """

    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocks")
    blocked = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="blocked_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("blocker", "blocked")


class PostSubscription(models.Model):
    """
    Opt-in notification: subscriber gets notified whenever target publishes
    a new post. This is NOT a follow — it only affects notifications.
    """

    subscriber = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="post_subscriptions"
    )
    target = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="post_subscribers"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("subscriber", "target")
