import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import social_media.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_media_service.settings.base')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            social_media.routing.websocket_urlpatterns
        )
    ),
})
