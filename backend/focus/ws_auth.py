"""
JWT authentication middleware for Channels WebSockets.

Clients connect with ws://host/ws/...?token=<access_token>. We validate the
token with SimpleJWT and attach the user to the scope; anonymous connections
are rejected by the consumers themselves.
"""
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser


@database_sync_to_async
def get_user_from_token(raw_token):
    from django.contrib.auth import get_user_model
    from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
    from rest_framework_simplejwt.tokens import AccessToken

    User = get_user_model()
    try:
        token = AccessToken(raw_token)
        return User.objects.get(id=token["user_id"], is_active=True)
    except (InvalidToken, TokenError, User.DoesNotExist, KeyError):
        return AnonymousUser()


class JWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query = parse_qs(scope.get("query_string", b"").decode())
        token = query.get("token", [None])[0]
        scope["user"] = (
            await get_user_from_token(token) if token else AnonymousUser()
        )
        return await self.inner(scope, receive, send)
