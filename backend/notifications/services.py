"""
Single entry point for creating notifications: persists the row and pushes it
to the recipient's WebSocket group in one call.
"""
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Notification


def notification_payload(n: Notification) -> dict:
    return {
        "id": n.id,
        "kind": n.kind,
        "text": n.text,
        "post_id": n.post_id,
        "conversation_id": n.conversation_id,
        "is_read": n.is_read,
        "created_at": n.created_at.isoformat(),
        "actor": {
            "id": n.actor_id,
            "display_name": n.actor.display_name if n.actor else "",
            "avatar": n.actor.avatar.url if (n.actor and n.actor.avatar) else None,
        },
    }


def notify(recipient_id, kind, actor, text, post_id=None, conversation_id=None):
    n = Notification.objects.create(
        recipient_id=recipient_id,
        actor=actor,
        kind=kind,
        text=text,
        post_id=post_id,
        conversation_id=conversation_id,
    )
    layer = get_channel_layer()
    if layer is not None:
        async_to_sync(layer.group_send)(
            f"notifications_{recipient_id}",
            {"type": "notification.new", "payload": notification_payload(n)},
        )
    return n
