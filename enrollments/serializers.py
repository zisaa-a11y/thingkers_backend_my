from datetime import date

from rest_framework import serializers

from .models import Enrollment


class EnrollmentSerializer(serializers.ModelSerializer):
    _id = serializers.CharField(source="id", read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            "_id",
            "course",
            "name",
            "email",
            "phone",
            "dob",
            "gender",
            "address",
            "level",
            "batch",
            "experience",
            "agree",
            "createdAt",
        ]

    def validate_agree(self, value):
        if value is not True:
            raise serializers.ValidationError("You must accept the terms")
        return value

    def validate_phone(self, value):
        digits = "".join(ch for ch in value if ch.isdigit())
        if len(digits) < 10 or len(digits) > 15:
            raise serializers.ValidationError("Phone must contain 10 to 15 digits")
        return value

    def validate_dob(self, value):
        today = date.today()
        if value >= today:
            raise serializers.ValidationError("Date of birth must be in the past")

        age_years = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age_years < 10:
            raise serializers.ValidationError("Minimum age is 10 years")
        return value

    def validate_email(self, value):
        return value.lower().strip()


class EnrollmentFormOptionsSerializer(serializers.Serializer):
    pythonLevelOptions = serializers.ListField()
    preferredBatchOptions = serializers.ListField()
    courses = serializers.ListField()
    featuredContent = serializers.ListField()
