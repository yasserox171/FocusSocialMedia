from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("admin/agents", views.AdminAgentViewSet, basename="admin-agents")

urlpatterns = [
    path("admin/stats/", views.admin_stats),
    path("internal/agents/", views.internal_agents),
    path("internal/agent-token/", views.internal_agent_token),
    path("internal/agent-posted/", views.internal_agent_posted),
    path("", include(router.urls)),
]
