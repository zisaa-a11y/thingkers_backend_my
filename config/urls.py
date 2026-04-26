from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health_check(_request):
    return JsonResponse({"message": "API is working!"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api", health_check),
    path("api/", health_check),
    path("api/health", health_check),
    path("api/auth/", include("accounts.urls")),
    path("api/", include("enrollments.urls")),
]
