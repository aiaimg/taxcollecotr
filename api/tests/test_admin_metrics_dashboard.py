"""
Tests for Admin Metrics Dashboard

Validates that the monitoring dashboard and data endpoints are accessible.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from api.models import APIKey, APIAuditLog


class AdminMetricsDashboardTest(TestCase):
    """Test admin metrics dashboard functionality"""

    def setUp(self):
        """Set up test user and sample data"""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        self.client.login(username='admin', password='testpass123')

        # Create test API key
        self.api_key = APIKey.objects.create(
            name='Test Key',
            organization='Test Org',
            contact_email='test@example.com',
            is_active=True
        )

        # Create sample audit logs
        now = timezone.now()
        for i in range(10):
            APIAuditLog.objects.create(
                correlation_id=f'test-{i}',
                endpoint='/api/v1/test/',
                method='GET',
                status_code=200 if i < 8 else 400,
                duration_ms=100 + i * 10,
                client_ip='127.0.0.1',
                api_key=self.api_key,
                timestamp=now - timedelta(minutes=i)
            )

    def test_metrics_dashboard_accessible(self):
        """Test that metrics dashboard page loads"""
        response = self.client.get(reverse('admin-metrics'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'API Metrics')
        self.assertContains(response, 'Usage by API Key')

    def test_metrics_usage_data_endpoint(self):
        """Test usage data endpoint returns JSON"""
        response = self.client.get(reverse('admin-metrics-usage'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        self.assertIn('usage_by_api_key', data)

    def test_metrics_error_data_endpoint(self):
        """Test error data endpoint returns JSON"""
        response = self.client.get(reverse('admin-metrics-errors'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('errors_by_status', data)

    def test_metrics_performance_data_endpoint(self):
        """Test performance data endpoint returns JSON"""
        response = self.client.get(reverse('admin-metrics-performance'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('performance', data)
        self.assertIsInstance(data['performance'], list)

    def test_metrics_timeseries_data_endpoint(self):
        """Test timeseries data endpoint returns JSON"""
        response = self.client.get(reverse('admin-metrics-timeseries'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('timestamps', data)
        self.assertIn('requests_per_min', data)
        self.assertIn('error_rate_percent', data)
        self.assertIn('avg_ms', data)
        self.assertIn('p95_ms', data)

    def test_metrics_top_endpoints_data_endpoint(self):
        """Test top endpoints data endpoint returns JSON"""
        response = self.client.get(reverse('admin-metrics-top'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('top_volume', data)
        self.assertIn('top_errors', data)

    def test_metrics_rate_limit_data_endpoint(self):
        """Test rate limit data endpoint returns JSON"""
        response = self.client.get(reverse('admin-metrics-rate-limit'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('rate_limited_by_api_key', data)

    def test_metrics_dashboard_requires_authentication(self):
        """Test that dashboard requires admin authentication"""
        self.client.logout()
        response = self.client.get(reverse('admin-metrics'))
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)

    def test_prometheus_metrics_endpoint_accessible(self):
        """Test that Prometheus metrics endpoint is accessible"""
        response = self.client.get(reverse('prometheus-metrics'))
        self.assertEqual(response.status_code, 200)
        # Check for Prometheus format
        content = response.content.decode('utf-8')
        self.assertIn('# HELP', content)
        self.assertIn('# TYPE', content)
        # Check for our custom metrics
        self.assertIn('api_request_total', content)
