from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse("user:create")
ME_URL = reverse("user:manage_user")
TOKEN_URL = reverse("user:token_obtain_pair")
TOKEN_REFRESH_URL = reverse("user:token_refresh")
TOKEN_VERIFY_URL = reverse("user:token_verify")

User = get_user_model()


class PublicUserApiTests(TestCase):
    """Tests for unauthenticated user actions"""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        payload = {"email": "test@test.com", "password": "testpass123"}
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))

    def test_create_user_short_password_fails(self):
        payload = {"email": "test@test.com", "password": "123"}
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_jwt_token_obtain_success(self):
        user = User.objects.create_user(email="test@test.com", password="testpass123")
        payload = {"email": "test@test.com", "password": "testpass123"}
        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

    def test_jwt_token_obtain_fail(self):
        payload = {"email": "wrong@test.com", "password": "wrongpass"}
        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_jwt_token_refresh(self):
        user = User.objects.create_user(email="test@test.com", password="testpass123")
        res_obtain = self.client.post(TOKEN_URL, {"email": user.email, "password": "testpass123"})
        refresh_token = res_obtain.data["refresh"]
        res_refresh = self.client.post(TOKEN_REFRESH_URL, {"refresh": refresh_token})
        self.assertEqual(res_refresh.status_code, status.HTTP_200_OK)
        self.assertIn("access", res_refresh.data)

    def test_jwt_token_verify_valid(self):
        user = User.objects.create_user(email="test@test.com", password="testpass123")
        res_obtain = self.client.post(TOKEN_URL, {"email": user.email, "password": "testpass123"})
        access_token = res_obtain.data["access"]
        res_verify = self.client.post(TOKEN_VERIFY_URL, {"token": access_token})
        self.assertEqual(res_verify.status_code, status.HTTP_200_OK)

    def test_jwt_token_verify_invalid(self):
        res = self.client.post(TOKEN_VERIFY_URL, {"token": "invalidtoken"})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Tests for authenticated user actions"""

    def setUp(self):
        self.user = User.objects.create_user(email="test@test.com", password="testpass123")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile(self):
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], self.user.email)

    def test_update_profile(self):
        payload = {"email": "new@test.com", "password": "newpass123"}
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, payload["email"])
        self.assertTrue(self.user.check_password(payload["password"]))

    def test_me_requires_authentication(self):
        client = APIClient()  # unauthenticated
        res = client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
