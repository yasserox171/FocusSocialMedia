from django.db.models import Count, Q
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from accounts.models import User
from accounts.permissions import IsAdmin
from rest_framework.decorators import permission_classes as perm

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .services import send_message


def _get_conversation_or_403(request, pk):
    try:
        conv = Conversation.objects.get(pk=pk)
    except Conversation.DoesNotExist:
        return None, Response(status=status.HTTP_404_NOT_FOUND)
    if not conv.includes(request.user):
        return None, Response(status=status.HTTP_403_FORBIDDEN)
    return conv, None


@api_view(["GET", "POST"])
def conversations(request):
    """GET: my conversations. POST {user_id}: open (or fetch) a conversation."""
    if request.method == "POST":
        try:
            other = User.objects.get(id=request.data.get("user_id"), is_active=True)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if other == request.user:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        conv = Conversation.between(request.user, other)
        return Response(
            ConversationSerializer(conv, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    qs = (
        Conversation.objects.filter(Q(user_a=request.user) | Q(user_b=request.user))
        .select_related("user_a", "user_b")
        .annotate(
            unread_count=Count(
                "messages",
                filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user),
            )
        )
    )
    return Response(
        ConversationSerializer(qs, many=True, context={"request": request}).data
    )


@api_view(["GET", "POST"])
def conversation_messages(request, pk):
    """GET: messages (paginated, newest page first). POST {text}: send via REST."""
    conv, err = _get_conversation_or_403(request, pk)
    if err:
        return err

    if request.method == "POST":
        text = (request.data.get("text") or "").strip()
        if not text:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        message = send_message(conv, request.user, text)
        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)

    qs = conv.messages.order_by("-created_at")
    paginator = PageNumberPagination()
    paginator.page_size = 50
    page = paginator.paginate_queryset(qs, request)
    return paginator.get_paginated_response(
        MessageSerializer(reversed(page), many=True).data
    )


@api_view(["POST"])
def mark_read(request, pk):
    conv, err = _get_conversation_or_403(request, pk)
    if err:
        return err
    conv.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "DELETE"])
@perm([IsAdmin])
def admin_messages(request, pk=None):
    """Moderation: list latest messages / delete an offending one."""
    if request.method == "DELETE":
        Message.objects.filter(pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    qs = Message.objects.select_related("sender").order_by("-created_at")
    paginator = PageNumberPagination()
    paginator.page_size = 50
    page = paginator.paginate_queryset(qs, request)
    data = [
        {
            **MessageSerializer(m).data,
            "sender_name": m.sender.display_name,
        }
        for m in page
    ]
    return paginator.get_paginated_response(data)
