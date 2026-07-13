from django.urls import path

from . import views

urlpatterns = [
    path("conversations/", views.conversations),
    path("conversations/<int:pk>/messages/", views.conversation_messages),
    path("conversations/<int:pk>/read/", views.mark_read),
    path("admin/messages/", views.admin_messages),
    path("admin/messages/<int:pk>/", views.admin_messages),
]
