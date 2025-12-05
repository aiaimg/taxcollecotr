"""
Tests for API Authentication
"""

from django.contrib.auth.models import User
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


class AuthenticationTestCase(TestCase):
    """Test authentication endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

    def test_login_success(self):
        """Test successful login"""
        response = self.client.post("/api/v1/auth/login/", {"email": "test@example.com", "password": "testpass123"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("access", response.data["data"])
        self.assertIn("refresh", response.data["data"])
        self.assertIn("user", response.data["data"])

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post("/api/v1/auth/login/", {"email": "test@example.com", "password": "wrongpassword"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_refresh_token(self):
        """Test token refresh"""
        refresh = RefreshToken.for_user(self.user)

        response = self.client.post("/api/v1/auth/refresh/", {"refresh": str(refresh)})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("access", response.data["data"])

    def test_logout(self):
        """Test logout"""
        refresh = RefreshToken.for_user(self.user)
        access_token = refresh.access_token

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        response = self.client.post("/api/v1/auth/logout/", {"refresh": str(refresh)})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token"""
        response = self.client.get("/api/v1/users/me/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_endpoint_with_token(self):
        """Test accessing protected endpoint with token"""
        refresh = RefreshToken.for_user(self.user)
        access_token = refresh.access_token

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        response = self.client.get("/api/v1/users/me/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
