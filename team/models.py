import uuid

from django.db import models


def team_profile_upload_path(_instance, filename):
    extension = filename.split(".")[-1].lower() if "." in filename else "jpg"
    return f"team/profile/{uuid.uuid4()}.{extension}"


class TeamMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)
    short_title = models.CharField(max_length=255, blank=True)
    email = models.EmailField(unique=True)
    profile_image = models.ImageField(upload_to=team_profile_upload_path)
    short_description = models.CharField(max_length=400)
    full_description = models.TextField()
    display_order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "full_name", "created_at"]

    def __str__(self):
        return f"{self.full_name} ({self.designation})"
