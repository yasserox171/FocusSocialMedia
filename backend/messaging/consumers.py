import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Conversation


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Real-time channel for one conversation.
    Client → server: {"type": "message", "text": "..."} or {"type": "typing"}.
    Server → client: {"type": "message", "data": {...}} / {"type": "typing", "user_id": N}.
    """

    async def connect(self):
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close(code=4001)
            return
        self.conversation_id = int(self.scope["url_route"]["kwargs"]["conversation_id"])
        allowed = await self._is_participant(user.id, self.conversation_id)
        if not allowed:
            await self.close(code=4003)
            return
        self.group = f"chat_{self.conversation_id}"
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, "group"):
            await self.channel_layer.group_discard(self.group, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
        except (TypeError, ValueError):
            return
        if data.get("type") == "message" and data.get("text", "").strip():
            await self._create_message(
                self.scope["user"].id, self.conversation_id, data["text"].strip()
            )
        elif data.get("type") == "typing":
            await self.channel_layer.group_send(
                self.group,
                {"type": "chat.typing", "user_id": self.scope["user"].id},
            )

    # --- group event handlers ---

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(
            {"type": "message", "data": event["payload"]}, ensure_ascii=False
        ))

    async def chat_typing(self, event):
        if event["user_id"] != self.scope["user"].id:
            await self.send(text_data=json.dumps(
                {"type": "typing", "user_id": event["user_id"]}
            ))

    # --- db helpers ---

    @database_sync_to_async
    def _is_participant(self, user_id, conversation_id):
        return Conversation.objects.filter(id=conversation_id).filter(
            user_a_id=user_id
        ).exists() or Conversation.objects.filter(
            id=conversation_id, user_b_id=user_id
        ).exists()

    @database_sync_to_async
    def _create_message(self, user_id, conversation_id, text):
        from django.contrib.auth import get_user_model

        from .services import send_message

        conv = Conversation.objects.get(id=conversation_id)
        sender = get_user_model().objects.get(id=user_id)
        send_message(conv, sender, text)
