from django.conf import settings
from django.db import models


class Post(models.Model):
    """
    A feed post. Any combination of text / image / video / external link is
    allowed (mixed posts). Comments are intentionally absent in V1 — add a
    Comment model with a FK to Post when needed; nothing here blocks it.
    """

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    text = models.TextField(blank=True, default="")
    image = models.ImageField(upload_to="posts/images/", null=True, blank=True)
    video = models.FileField(upload_to="posts/videos/", null=True, blank=True)
    link_url = models.URLField(blank=True, default="")
    link_title = models.CharField(max_length=300, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author} — {self.text[:40]}"


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes"
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")
