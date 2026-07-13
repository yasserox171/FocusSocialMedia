from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/", include("accounts.urls")),
    path("api/", include("posts.urls")),
    path("api/", include("messaging.urls")),
    path("api/", include("notifications.urls")),
    path("api/", include("aiagents.urls")),
]

if settings.DEBUG or True:
    # Media served by Django in dev; nginx serves /media in production compose.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
