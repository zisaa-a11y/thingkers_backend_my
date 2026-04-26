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

    def test_create_enrollment(self):
        response = self.client.post("/api/python", self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Enrollment saved successfully")
        self.assertTrue(Enrollment.objects.filter(email="jane@example.com").exists())

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

        delete_response = self.client.delete(
            f"/api/admin/enrollments/{enrollment.id}",
            HTTP_X_ADMIN_TOKEN=settings.ADMIN_TOKEN,
        )

        self.assertEqual(delete_response.status_code, status.HTTP_200_OK)
        self.assertFalse(Enrollment.objects.filter(id=enrollment.id).exists())
