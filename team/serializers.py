from django.conf import settings
from rest_framework import serializers

from .models import TeamMember


class TeamMemberSerializer(serializers.ModelSerializer):
    _id = serializers.CharField(source="id", read_only=True)
    fullName = serializers.CharField(source="full_name")
    shortTitle = serializers.CharField(source="short_title", allow_blank=True)
    profileImage = serializers.ImageField(source="profile_image", required=False, allow_null=True)
    shortDescription = serializers.CharField(source="short_description")
    fullDescription = serializers.CharField(source="full_description")
    displayOrder = serializers.IntegerField(source="display_order")
    isActive = serializers.BooleanField(source="is_active", required=False)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = TeamMember
        fields = [
            "_id",
            "fullName",
            "designation",
            "shortTitle",
            "email",
            "profileImage",
            "shortDescription",
            "fullDescription",
            "displayOrder",
            "isActive",
            "createdAt",
            "updatedAt",
        ]

    def validate_email(self, value):
        return value.strip().lower()

    def validate_displayOrder(self, value):
        if value < 0:
            raise serializers.ValidationError("Display order must be 0 or greater")
        return value

    def validate(self, attrs):
        if self.instance is None and attrs.get("profile_image") is None:
            raise serializers.ValidationError({"profileImage": "Profile image is required"})
        return attrs

    def validate_profileImage(self, value):
        if value is None:
            return value

        allowed_types = set(getattr(settings, "TEAM_ALLOWED_IMAGE_CONTENT_TYPES", set()))
        max_size = int(getattr(settings, "TEAM_MAX_IMAGE_SIZE_BYTES", 2 * 1024 * 1024))

        content_type = getattr(value, "content_type", "")
        if allowed_types and content_type not in allowed_types:
            raise serializers.ValidationError("Unsupported image format. Use JPG, PNG or WEBP.")

        if value.size > max_size:
            raise serializers.ValidationError("Image file is too large.")

        return value


class TeamMemberStatusSerializer(serializers.Serializer):
    isActive = serializers.BooleanField()


class TeamMemberReorderItemSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    displayOrder = serializers.IntegerField(min_value=0)


class TeamMemberReorderSerializer(serializers.Serializer):
    items = TeamMemberReorderItemSerializer(many=True)
