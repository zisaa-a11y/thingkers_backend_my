from django.contrib import admin

from .models import Enrollment


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "course",
        "level",
        "batch",
        "experience",
        "created_at",
    )
    list_filter = ("course", "level", "batch", "experience", "gender", "created_at")
    search_fields = ("name", "email", "phone")
    ordering = ("-created_at",)
