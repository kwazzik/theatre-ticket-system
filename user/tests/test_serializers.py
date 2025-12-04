from django.test import TestCase
from django.contrib.auth import get_user_model
from user.serializers import UserSerializer, AuthTokenSerializer
from rest_framework.serializers import ValidationError

User = get_user_model()

class UserSerializerTests(TestCase):
    def test_create_user_success(self):
        payload = {"email": "test@test.com", "password": "pass123"}
        serializer = UserSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        self.assertEqual(user.email, payload["email"])
        self.assertTrue(user.check_password(payload["password"]))

    def test_update_user_password_hashed(self):
        user = User.objects.create_user(email="test@test.com", password="oldpass")
        payload = {"password": "newpass123"}
        serializer = UserSerializer(user, data=payload, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_user = serializer.save()

        self.assertTrue(updated_user.check_password(payload["password"]))

    def test_create_user_short_password_fails(self):
        payload = {"email": "test@test.com", "password": "123"}
        serializer = UserSerializer(data=payload)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)


class AuthTokenSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@test.com", password="testpass123")

    def test_valid_auth_returns_user(self):
        serializer = AuthTokenSerializer(data={"email": "test@test.com", "password": "testpass123"})
        serializer.is_valid(raise_exception=True)
        self.assertEqual(serializer.validated_data["user"], self.user)

    def test_invalid_password_raises_error(self):
        serializer = AuthTokenSerializer(data={"email": "test@test.com", "password": "wrongpass"})
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_missing_email_raises_error(self):
        serializer = AuthTokenSerializer(data={"password": "testpass123"})
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_missing_password_raises_error(self):
        serializer = AuthTokenSerializer(data={"email": "test@test.com"})
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
