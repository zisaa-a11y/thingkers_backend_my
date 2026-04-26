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
