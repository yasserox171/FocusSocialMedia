from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Notification
from .services import notification_payload


@api_view(["GET"])
def list_notifications(request):
    qs = Notification.objects.filter(recipient=request.user).select_related("actor")
    paginator = PageNumberPagination()
    page = paginator.paginate_queryset(qs, request)
    return paginator.get_paginated_response([notification_payload(n) for n in page])


@api_view(["GET"])
def unread_count(request):
    return Response({
        "count": Notification.objects.filter(recipient=request.user, is_read=False).count()
    })


@api_view(["POST"])
def mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return Response(status=status.HTTP_204_NO_CONTENT)
