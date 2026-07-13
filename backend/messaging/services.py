"""
Message creation shared by the REST endpoint and the WebSocket consumer:
persists the message, fans it out to the conversation group, and raises a
notification for the recipient.
"""
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from notifications.services import notify

from .models import Conversation, Message


def message_payload(m: Message) -> dict:
    return {
        "id": m.id,
        "conversation": m.conversation_id,
        "sender": m.sender_id,
        "text": m.text,
        "created_at": m.created_at.isoformat(),
        "is_read": m.is_read,
    }


def send_message(conversation: Conversation, sender, text: str) -> Message:
    message = Message.objects.create(
        conversation=conversation, sender=sender, text=text
    )
    conversation.save(update_fields=["updated_at"])  # bump ordering

    layer = get_channel_layer()
    if layer is not None:
        async_to_sync(layer.group_send)(
            f"chat_{conversation.id}",
            {"type": "chat.message", "payload": message_payload(message)},
        )

    recipient = conversation.other(sender)
    notify(
        recipient_id=recipient.id,
        kind="message",
        actor=sender,
        text=f"رسالة جديدة من {sender.display_name}",
        conversation_id=conversation.id,
    )
    return message
