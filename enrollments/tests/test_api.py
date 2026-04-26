from django.conf import settings
from rest_framework import status
from rest_framework.test import APITestCase

from enrollments.models import Enrollment


class EnrollmentAPITests(APITestCase):
    def setUp(self):
        self.payload = {
            "course": "Python",
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "0123456789",
            "dob": "2000-01-01",
            "gender": "female",
            "address": "Dhaka",
            "level": "beginner",
            "batch": "morning",
            "experience": "no",
            "agree": True,
        }

    def test_form_options_exact_values(self):
        response = self.client.get("/api/enrollment/form-options")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["label"] for item in response.data["pythonLevelOptions"]],
            ["Beginner", "Intermediate", "Advance"],
        )
        self.assertEqual(
            [item["label"] for item in response.data["preferredBatchOptions"]],
            ["Morning", "Evening", "Weekend"],
        )

    def test_create_enrollment(self):
        response = self.client.post("/api/python", self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Enrollment saved successfully")
        self.assertEqual(response.data["data"]["level"], "beginner")
        self.assertTrue(Enrollment.objects.filter(email="jane@example.com").exists())

    def test_create_enrollment_with_advance_level(self):
        payload = {**self.payload, "email": "advance@example.com", "level": "advance"}
        response = self.client.post("/api/python", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        saved = Enrollment.objects.get(email="advance@example.com")
        self.assertEqual(saved.level, "advance")

    def test_create_enrollment_with_invalid_level_fails(self):
        payload = {**self.payload, "email": "invalid@example.com", "level": "advanced"}
        response = self.client.post("/api/python", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("level", response.data)

    def test_admin_list_requires_token(self):
        response = self.client.get("/api/admin/enrollments")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_list_and_delete_with_token(self):
        enrollment = Enrollment.objects.create(**self.payload)

        response = self.client.get(
            "/api/admin/enrollments",
            HTTP_X_ADMIN_TOKEN=settings.ADMIN_TOKEN,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

        paged_response = self.client.get(
            "/api/admin/enrollments?page=1&limit=10",
            HTTP_X_ADMIN_TOKEN=settings.ADMIN_TOKEN,
        )
        self.assertEqual(paged_response.status_code, status.HTTP_200_OK)
        self.assertIn("data", paged_response.data)
        self.assertIn("total", paged_response.data)

        delete_response = self.client.delete(
            f"/api/admin/enrollments/{enrollment.id}",
            HTTP_X_ADMIN_TOKEN=settings.ADMIN_TOKEN,
        )

        self.assertEqual(delete_response.status_code, status.HTTP_200_OK)
        self.assertFalse(Enrollment.objects.filter(id=enrollment.id).exists())
