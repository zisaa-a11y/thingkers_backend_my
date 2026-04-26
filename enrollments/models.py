import uuid

from django.db import models


class Enrollment(models.Model):
    GENDER_CHOICES = (
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    )

    LEVEL_CHOICES = (
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    )

    BATCH_CHOICES = (
        ("morning", "Morning"),
        ("evening", "Evening"),
        ("weekend", "Weekend"),
    )

    EXPERIENCE_CHOICES = (
        ("yes", "Yes"),
        ("no", "No"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.CharField(max_length=120)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    dob = models.DateField()
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    address = models.TextField()
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    batch = models.CharField(max_length=20, choices=BATCH_CHOICES)
    experience = models.CharField(max_length=10, choices=EXPERIENCE_CHOICES)
    agree = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} - {self.course}"
