from django.urls import path

from . import views

urlpatterns = [
    path("notifications/", views.list_notifications),
    path("notifications/unread-count/", views.unread_count),
    path("notifications/read-all/", views.mark_all_read),
]
