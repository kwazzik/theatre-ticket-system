from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:login")
ME_URL = reverse("user:me")

User = get_user_model()

class PublicUserApiTests(TestCase):
    """Tests for unauthenticated user API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        payload = {"email": "test@test.com", "password": "testpass123"}
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, 201)
        user = User.objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))

    def test_create_user_invalid_password(self):
        payload = {"email": "test@test.com", "password": "pw"}
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, 400)

    def test_login_user_success(self):
        payload = {"username": "test@test.com", "password": "testpass123"}
        User.objects.create_user(**{"email": payload["username"], "password": payload["password"]})
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, 200)

    def test_login_user_invalid(self):
        res = self.client.post(TOKEN_URL, {"username": "wrong@test.com", "password": "pw"})
        self.assertEqual(res.status_code, 400)


class PrivateUserApiTests(TestCase):
    """Tests for authenticated user API"""

    def setUp(self):
        self.user = User.objects.create_user(email="test@test.com", password="testpass123")
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_profile(self):
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["email"], self.user.email)

    def test_update_profile(self):
        payload = {"email": "new@test.com", "password": "newpass123"}
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, payload["email"])
        self.assertTrue(self.user.check_password(payload["password"]))
