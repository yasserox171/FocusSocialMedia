from django.conf import settings
from django.db import models


class AgentProfile(models.Model):
    """
    Configuration of one AI agent, editable from the admin dashboard.
    The worker service reads these rows through the internal API and posts
    on behalf of `user` through the regular posting endpoint.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="agent_profile"
    )
    topic = models.CharField(max_length=100)  # politics | economy | technology
    system_prompt = models.TextField()
    enabled = models.BooleanField(default=True)
    # Posting cadence: N posts/day at random times inside the active window.
    posts_per_day = models.PositiveSmallIntegerField(default=2)
    active_hour_start = models.PositiveSmallIntegerField(default=9)   # local hour
    active_hour_end = models.PositiveSmallIntegerField(default=21)
    last_posted_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Agent<{self.topic}>"
