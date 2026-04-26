from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User


class AuthAPITests(APITestCase):
    def test_register_creates_user_and_returns_token(self):
        response = self.client.post(
            "/api/auth/register",
            {
                "fullName": "Test User",
                "email": "test@example.com",
                "password": "Password123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertIn("accessToken", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["email"], "test@example.com")
        self.assertTrue(User.objects.filter(email="test@example.com").exists())
        self.assertIn("refresh_token", response.cookies)

    def test_login_returns_token_for_existing_user(self):
        User.objects.create_user(
            email="login@example.com",
            full_name="Login User",
            password="Password123!",
        )

        response = self.client.post(
            "/api/auth/login",
            {"email": "login@example.com", "password": "Password123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertIn("accessToken", response.data)
        self.assertEqual(response.data["user"]["email"], "login@example.com")
        self.assertIn("refresh_token", response.cookies)

    def test_register_rejects_duplicate_email(self):
        User.objects.create_user(
            email="dup@example.com",
            full_name="Original User",
            password="Password123!",
        )

        response = self.client.post(
            "/api/auth/register",
            {
                "fullName": "Duplicate User",
                "email": "dup@example.com",
                "password": "Password123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_refresh_and_me_flow(self):
        User.objects.create_user(
            email="flow@example.com",
            full_name="Flow User",
            password="Password123!",
        )

        login = self.client.post(
            "/api/auth/login",
            {"email": "flow@example.com", "password": "Password123!"},
            format="json",
        )
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        access_token = login.data["accessToken"]

        me = self.client.get(
            "/api/auth/me",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        self.assertEqual(me.data["user"]["email"], "flow@example.com")

        refresh = self.client.post("/api/auth/refresh", format="json")
        self.assertEqual(refresh.status_code, status.HTTP_200_OK)
        self.assertIn("accessToken", refresh.data)

    def test_logout_clears_refresh_cookie(self):
        User.objects.create_user(
            email="logout@example.com",
            full_name="Logout User",
            password="Password123!",
        )

        self.client.post(
            "/api/auth/login",
            {"email": "logout@example.com", "password": "Password123!"},
            format="json",
        )

        logout = self.client.post("/api/auth/logout", format="json")
        self.assertEqual(logout.status_code, status.HTTP_200_OK)
        self.assertEqual(logout.cookies["refresh_token"].value, "")

    def test_login_lockout_after_repeated_failures(self):
        User.objects.create_user(
            email="lock@example.com",
            full_name="Lock User",
            password="Password123!",
        )

        for _ in range(5):
            response = self.client.post(
                "/api/auth/login",
                {"email": "lock@example.com", "password": "wrong-pass"},
                format="json",
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        blocked = self.client.post(
            "/api/auth/login",
            {"email": "lock@example.com", "password": "wrong-pass"},
            format="json",
        )
        self.assertEqual(blocked.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
