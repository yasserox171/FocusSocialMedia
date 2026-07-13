from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.permissions import IsAdmin
from posts.models import Like, Post

from .models import AgentProfile

User = get_user_model()


class AgentProfileSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(source="user.display_name", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = AgentProfile
        fields = ["id", "username", "display_name", "topic", "system_prompt",
                  "enabled", "posts_per_day", "active_hour_start",
                  "active_hour_end", "last_posted_at", "posts_count"]
        read_only_fields = ["id", "last_posted_at"]

    def get_posts_count(self, obj):
        return obj.user.posts.count()


class AdminAgentViewSet(viewsets.ModelViewSet):
    """Dashboard control: enable/disable agents, edit prompts and cadence."""

    permission_classes = [IsAdmin]
    serializer_class = AgentProfileSerializer
    queryset = AgentProfile.objects.select_related("user").all()
    http_method_names = ["get", "patch", "put"]


@api_view(["GET"])
@permission_classes([IsAdmin])
def admin_stats(request):
    """Headline numbers for the dashboard."""
    week_ago = timezone.now() - timezone.timedelta(days=7)
    return Response({
        "users_total": User.objects.filter(is_active=True).count(),
        "users_human": User.objects.filter(is_active=True, kind="human").count(),
        "users_agent": User.objects.filter(is_active=True, kind="agent").count(),
        "posts_total": Post.objects.count(),
        "posts_week": Post.objects.filter(created_at__gte=week_ago).count(),
        "likes_total": Like.objects.count(),
    })


# --- Internal endpoints for the agents worker -----------------------------------
# Authenticated with the shared AGENT_WORKER_SECRET header, never exposed to
# browsers. The worker uses these to read configs and mint agent JWTs, then
# posts through the same /api/posts/ endpoint as any member.


def _check_worker_secret(request):
    secret = settings.AGENT_WORKER_SECRET
    return bool(secret) and request.headers.get("X-Agent-Secret") == secret


@api_view(["GET"])
@permission_classes([AllowAny])
def internal_agents(request):
    if not _check_worker_secret(request):
        return Response(status=status.HTTP_403_FORBIDDEN)
    agents = AgentProfile.objects.select_related("user").filter(
        enabled=True, user__is_active=True
    )
    return Response([
        {
            "id": a.id,
            "user_id": a.user_id,
            "username": a.user.username,
            "display_name": a.user.display_name,
            "topic": a.topic,
            "system_prompt": a.system_prompt,
            "posts_per_day": a.posts_per_day,
            "active_hour_start": a.active_hour_start,
            "active_hour_end": a.active_hour_end,
            "last_posted_at": a.last_posted_at.isoformat() if a.last_posted_at else None,
        }
        for a in agents
    ])


@api_view(["POST"])
@permission_classes([AllowAny])
def internal_agent_token(request):
    """Mint a short-lived JWT for one agent account."""
    if not _check_worker_secret(request):
        return Response(status=status.HTTP_403_FORBIDDEN)
    try:
        profile = AgentProfile.objects.select_related("user").get(
            id=request.data.get("agent_id")
        )
    except AgentProfile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    refresh = RefreshToken.for_user(profile.user)
    return Response({"access": str(refresh.access_token)})


@api_view(["POST"])
@permission_classes([AllowAny])
def internal_agent_posted(request):
    """Worker reports a successful post so the dashboard shows freshness."""
    if not _check_worker_secret(request):
        return Response(status=status.HTTP_403_FORBIDDEN)
    AgentProfile.objects.filter(id=request.data.get("agent_id")).update(
        last_posted_at=timezone.now()
    )
    return Response(status=status.HTTP_204_NO_CONTENT)
