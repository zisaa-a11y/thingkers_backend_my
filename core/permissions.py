from django.conf import settings
from rest_framework.permissions import BasePermission


class HasAdminToken(BasePermission):
    message = "Unauthorized"

    def has_permission(self, request, view):
        header_token = request.headers.get("x-admin-token")
        admin_token = getattr(settings, "ADMIN_TOKEN", "")
        if admin_token and header_token and header_token == admin_token:
            return True

        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and getattr(user, "role", None) == "admin")
