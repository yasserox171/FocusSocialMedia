from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Platform administrators (Django is_staff)."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)
