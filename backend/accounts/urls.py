from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("users", views.UserViewSet, basename="users")
router.register("admin/users", views.AdminUserViewSet, basename="admin-users")
router.register("admin/invites", views.AdminInviteViewSet, basename="admin-invites")

urlpatterns = [
    path("users/me/", views.MeView.as_view()),
    path("users/relations/", views.my_relations),
    path("auth/invite/accept/", views.invite_accept),
    path("auth/invite/<str:token>/", views.invite_info),
    path("", include(router.urls)),
]
