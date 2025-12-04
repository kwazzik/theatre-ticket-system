from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserManagerTests(TestCase):
    def test_create_user_successful(self):
        email = "user@test.com"
        password = "pass123"
        user = User.objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password(password))

    def test_create_user_no_email_raises(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email=None, password="pass123")

    def test_create_superuser_successful(self):
        email = "admin@test.com"
        password = "admin123"
        admin = User.objects.create_superuser(email=email, password=password)

        self.assertEqual(admin.email, email)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.check_password(password))

    def test_create_superuser_is_staff_false_raises(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email="admin2@test.com", password="pass123", is_staff=False)

    def test_create_superuser_is_superuser_false_raises(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email="admin3@test.com", password="pass123", is_superuser=False)


class UserModelTests(TestCase):
    def test_username_field_is_email(self):
        self.assertEqual(User.USERNAME_FIELD, "email")
