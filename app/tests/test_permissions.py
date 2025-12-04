from django.test import TestCase
from rest_framework.test import APIRequestFactory
from app.permissions import IsAdminOrIfAuthenticatedReadOnly
from django.contrib.auth import get_user_model

class IsAdminOrIfAuthenticatedReadOnlyTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = IsAdminOrIfAuthenticatedReadOnly()
        self.user = get_user_model().objects.create_user("user@test.com", "pass123")
        self.admin = get_user_model().objects.create_user(
            "admin@test.com", "pass123", is_staff=True
        )

    def test_safe_method_authenticated_user_allowed(self):
        request = self.factory.get("/")
        request.user = self.user
        self.assertTrue(self.permission.has_permission(request, None))

    def test_safe_method_unauthenticated_user_denied(self):
        request = self.factory.get("/")
        request.user = None
        self.assertFalse(self.permission.has_permission(request, None))

    def test_safe_method_admin_allowed(self):
        request = self.factory.get("/")
        request.user = self.admin
        self.assertTrue(self.permission.has_permission(request, None))

    def test_unsafe_method_user_denied(self):
        request = self.factory.post("/")
        request.user = self.user
        self.assertFalse(self.permission.has_permission(request, None))

    def test_unsafe_method_admin_allowed(self):
        request = self.factory.post("/")
        request.user = self.admin
        self.assertTrue(self.permission.has_permission(request, None))
