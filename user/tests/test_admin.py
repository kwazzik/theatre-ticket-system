from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from user.admin import UserAdmin
from user.models import User

class MockRequest:
    pass

class UserAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.user_admin = UserAdmin(User, self.site)

    def test_fieldsets(self):
        self.assertIn(('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}), self.user_admin.fieldsets)

    def test_add_fieldsets(self):
        self.assertEqual(self.user_admin.add_fieldsets[0][1]['fields'], ('email', 'password1', 'password2'))

    def test_list_display(self):
        self.assertEqual(self.user_admin.list_display, ('email', 'first_name', 'last_name', 'is_staff'))

    def test_search_fields(self):
        self.assertEqual(self.user_admin.search_fields, ('email', 'first_name', 'last_name'))

    def test_ordering(self):
        self.assertEqual(self.user_admin.ordering, ('email',))
