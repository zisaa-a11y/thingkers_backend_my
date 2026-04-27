from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


def health_check(_request):
    return JsonResponse({"message": "API is working!"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api", health_check),
    path("api/", health_check),
    path("api/health", health_check),
    path("api/health/", health_check),
    path("api/auth/", include("accounts.urls")),
    path("api/", include("enrollments.urls")),
    path("api/", include("team.urls")),
]

if settings.DEBUG or settings.SERVE_MEDIA_FILES:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
