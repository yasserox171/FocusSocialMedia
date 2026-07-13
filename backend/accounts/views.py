from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Block, Invite, PostSubscription, User
from .permissions import IsAdmin
from .serializers import (
    AdminUserSerializer,
    InviteAcceptSerializer,
    InviteSerializer,
    UserSerializer,
)


class MeView(APIView):
    """Current user's profile: read and update (name, bio, avatar)."""

    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        return Response(UserSerializer(request.user, context={"request": request}).data)

    def patch(self, request):
        serializer = UserSerializer(
            request.user, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Member directory + block / subscription actions."""

    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(is_active=True).order_by("display_name")

    @action(detail=True, methods=["post", "delete"])
    def block(self, request, pk=None):
        target = self.get_object()
        if target == request.user:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.method == "POST":
            Block.objects.get_or_create(blocker=request.user, blocked=target)
        else:
            Block.objects.filter(blocker=request.user, blocked=target).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post", "delete"])
    def subscribe(self, request, pk=None):
        """Toggle 'notify me on new posts from this account'."""
        target = self.get_object()
        if target == request.user:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.method == "POST":
            PostSubscription.objects.get_or_create(subscriber=request.user, target=target)
        else:
            PostSubscription.objects.filter(
                subscriber=request.user, target=target
            ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
def my_relations(request):
    """IDs the client needs to render block/subscribe buttons in one call."""
    return Response({
        "blocked_ids": list(
            Block.objects.filter(blocker=request.user).values_list("blocked_id", flat=True)
        ),
        "subscribed_ids": list(
            PostSubscription.objects.filter(subscriber=request.user)
            .values_list("target_id", flat=True)
        ),
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def invite_info(request, token):
    """Public: show the invitee's name on the accept-invite page."""
    try:
        invite = Invite.objects.get(token=token, used_by__isnull=True)
    except Invite.DoesNotExist:
        return Response({"detail": "دعوة غير صالحة."}, status=status.HTTP_404_NOT_FOUND)
    return Response({"display_name": invite.display_name})


@api_view(["POST"])
@permission_classes([AllowAny])
def invite_accept(request):
    """Public: turn a valid invite into a real account."""
    serializer = InviteAcceptSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    try:
        invite = Invite.objects.get(token=data["token"], used_by__isnull=True)
    except Invite.DoesNotExist:
        return Response({"detail": "دعوة غير صالحة."}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(
        username=data["username"],
        password=data["password"],
        display_name=invite.display_name,
        kind=User.Kind.HUMAN,
    )
    invite.used_by = user
    invite.used_at = timezone.now()
    invite.save(update_fields=["used_by", "used_at"])
    return Response({"detail": "تم إنشاء الحساب. يمكنك تسجيل الدخول."},
                    status=status.HTTP_201_CREATED)


# --- Admin dashboard endpoints -------------------------------------------------


class AdminUserViewSet(viewsets.ModelViewSet):
    """Add / edit / disable / delete accounts from the dashboard."""

    permission_classes = [IsAdmin]
    serializer_class = AdminUserSerializer
    queryset = User.objects.all().order_by("-date_joined")
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class AdminInviteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = InviteSerializer
    queryset = Invite.objects.all().order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
