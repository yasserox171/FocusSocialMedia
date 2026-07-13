"""
ASGI entrypoint. HTTP is handled by Django; WebSockets are routed through
Channels with JWT authentication (token passed as ?token=<jwt> query param).
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "focus.settings")

# Initialise Django before importing anything that touches models.
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from channels.security.websocket import AllowedHostsOriginValidator  # noqa: E402

from focus.ws_auth import JWTAuthMiddleware  # noqa: E402
import messaging.routing  # noqa: E402
import notifications.routing  # noqa: E402

websocket_urlpatterns = (
    messaging.routing.websocket_urlpatterns
    + notifications.routing.websocket_urlpatterns
)

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": JWTAuthMiddleware(URLRouter(websocket_urlpatterns)),
    }
)
