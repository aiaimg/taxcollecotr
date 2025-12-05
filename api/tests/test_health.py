"""
Tests for Health Check endpoint
"""

from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient


class HealthCheckTestCase(TestCase):
    """Test health check endpoint"""

    def setUp(self):
        """Set up test client"""
        self.client = APIClient()

    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get("/api/v1/health/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["status"], "healthy")
        self.assertIn("checks", response.data["data"])
        self.assertIn("database", response.data["data"]["checks"])
        self.assertIn("cache", response.data["data"]["checks"])
