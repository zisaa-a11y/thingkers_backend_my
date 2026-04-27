from io import BytesIO

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from team.models import TeamMember


class TeamMemberAPITests(APITestCase):
    def setUp(self):
        self.base_payload = {
            "fullName": "Test Member",
            "designation": "Lead Engineer",
            "shortTitle": "Founder & Architect",
            "email": "member@example.com",
            "shortDescription": "Short intro",
            "fullDescription": "Long team member biography",
            "displayOrder": 1,
            "isActive": True,
        }

    def create_image(self, name="profile.png", content_type="image/png"):
        buffer = BytesIO()
        Image.new("RGB", (1, 1), color="white").save(buffer, format="PNG")
        return SimpleUploadedFile(name, buffer.getvalue(), content_type=content_type)

    def create_member(self, **overrides):
        member = TeamMember.objects.create(
            full_name=overrides.get("full_name", "John Team"),
            designation=overrides.get("designation", "Architect"),
            short_title=overrides.get("short_title", "Founder"),
            email=overrides.get("email", "john@example.com"),
            profile_image=overrides.get("profile_image", self.create_image()),
            short_description=overrides.get("short_description", "Bio short"),
            full_description=overrides.get("full_description", "Bio full"),
            display_order=overrides.get("display_order", 0),
            is_active=overrides.get("is_active", True),
        )
        return member

    def test_public_list_returns_only_active_and_ordered(self):
        self.create_member(email="active2@example.com", full_name="B", display_order=2, is_active=True)
        self.create_member(email="active1@example.com", full_name="A", display_order=1, is_active=True)
        self.create_member(email="inactive@example.com", full_name="Z", display_order=0, is_active=False)

        response = self.client.get("/api/team-members")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["email"], "active1@example.com")
        self.assertEqual(response.data[1]["email"], "active2@example.com")

    def test_admin_create_requires_permission(self):
        response = self.client.post("/api/admin/team-members", self.base_payload, format="json")
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_admin_create_with_upload_and_list(self):
        payload = {**self.base_payload, "profileImage": self.create_image()}

        response = self.client.post(
            "/api/admin/team-members",
            payload,
            HTTP_X_ADMIN_TOKEN=settings.ADMIN_TOKEN,
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["data"]["email"], "member@example.com")
        self.assertTrue(TeamMember.objects.filter(email="member@example.com").exists())

        list_response = self.client.get(
            "/api/admin/team-members?page=1&limit=10&search=member",
            HTTP_X_ADMIN_TOKEN=settings.ADMIN_TOKEN,
        )
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data["total"], 1)

    def test_admin_create_rejects_invalid_image_type(self):
        payload = {
            **self.base_payload,
            "email": "invalid-image@example.com",
            "profileImage": SimpleUploadedFile("x.txt", b"not-image", content_type="text/plain"),
        }

        response = self.client.post(
            "/api/admin/team-members",
            payload,
            HTTP_X_ADMIN_TOKEN=settings.ADMIN_TOKEN,
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("profileImage", response.data)

    def test_admin_update_delete_toggle_and_reorder(self):
        member_a = self.create_member(email="a@example.com", display_order=10)
        member_b = self.create_member(email="b@example.com", full_name="Beta", display_order=20)

        update_response = self.client.patch(
            f"/api/admin/team-members/{member_a.id}",
            {"designation": "Chief AI Architect"},
            HTTP_X_ADMIN_TOKEN=settings.ADMIN_TOKEN,
            format="json",
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["data"]["designation"], "Chief AI Architect")

        toggle_response = self.client.patch(
            f"/api/admin/team-members/{member_a.id}/toggle-status",
            {"isActive": False},
            HTTP_X_ADMIN_TOKEN=settings.ADMIN_TOKEN,
            format="json",
        )
        self.assertEqual(toggle_response.status_code, status.HTTP_200_OK)
        self.assertFalse(toggle_response.data["data"]["isActive"])

        reorder_response = self.client.post(
            "/api/admin/team-members/reorder",
            {
                "items": [
                    {"id": str(member_a.id), "displayOrder": 2},
                    {"id": str(member_b.id), "displayOrder": 1},
                ]
            },
            HTTP_X_ADMIN_TOKEN=settings.ADMIN_TOKEN,
            format="json",
        )
        self.assertEqual(reorder_response.status_code, status.HTTP_200_OK)

        ordered = list(TeamMember.objects.filter(id__in=[member_a.id, member_b.id]).order_by("display_order"))
        self.assertEqual(ordered[0].id, member_b.id)

        delete_response = self.client.delete(
            f"/api/admin/team-members/{member_b.id}",
            HTTP_X_ADMIN_TOKEN=settings.ADMIN_TOKEN,
        )
        self.assertEqual(delete_response.status_code, status.HTTP_200_OK)
        self.assertFalse(TeamMember.objects.filter(id=member_b.id).exists())
