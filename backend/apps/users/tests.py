from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from tests.utils import generate_test_password

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.test_password = generate_test_password()
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': self.test_password
        }

    def test_create_user(self):
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(user.check_password(self.test_password))
        self.assertFalse(user.is_verified)
        self.assertTrue(user.created_at)
        self.assertTrue(user.updated_at)

    def test_create_user_with_duplicate_email(self):
        User.objects.create_user(**self.user_data)
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email='test@example.com',
                username='testuser2',
                first_name='Test2',
                last_name='User2',
                password=generate_test_password()
            )

    def test_user_string_representation(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'test@example.com')

    def test_email_as_username_field(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.USERNAME_FIELD, 'email')

    def test_required_fields(self):
        self.assertEqual(User.REQUIRED_FIELDS, ['username', 'first_name', 'last_name'])

    def test_user_defaults(self):
        user = User.objects.create_user(**self.user_data)
        self.assertFalse(user.is_verified)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_create_superuser(self):
        admin_password = generate_test_password()
        user = User.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            first_name='Admin',
            last_name='User',
            password=admin_password
        )
        
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_user_authentication_with_email(self):
        user = User.objects.create_user(**self.user_data)
        
        # Test authentication with email
        from django.contrib.auth import authenticate
        authenticated_user = authenticate(
            username='test@example.com',
            password=self.test_password
        )
        self.assertEqual(authenticated_user, user)

    def test_user_with_invalid_email(self):
        user_data = self.user_data.copy()
        user_data['email'] = 'invalid-email'
        
        user = User(**user_data)
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_user_without_required_fields(self):
        with self.assertRaises(TypeError):
            User.objects.create_user(
                email='test@example.com',
                password=self.test_password
            )

    def test_user_timestamps(self):
        user = User.objects.create_user(**self.user_data)
        created_at = user.created_at
        updated_at = user.updated_at
        
        # Update user
        user.first_name = 'Updated'
        user.save()
        user.refresh_from_db()
        
        # created_at should remain the same, updated_at should change
        self.assertEqual(user.created_at, created_at)
        self.assertNotEqual(user.updated_at, updated_at)


class UserAPITest(APITestCase):
    def setUp(self):
        test_password = generate_test_password()
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': test_password
        }
        self.user = User.objects.create_user(**self.user_data)
        self.profile_url = reverse('users:profile')

    def test_get_user_profile_authenticated(self):
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['first_name'], 'Test')
        self.assertEqual(response.data['last_name'], 'User')

    def test_get_user_profile_unauthenticated(self):
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_profile(self):
        self.client.force_authenticate(user=self.user)
        
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        response = self.client.patch(self.profile_url, update_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['last_name'], 'Name')
        
        # Verify database was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')

    def test_update_user_profile_invalid_data(self):
        self.client.force_authenticate(user=self.user)
        
        update_data = {
            'email': 'invalid-email'
        }
        
        response = self.client.patch(self.profile_url, update_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_profile_duplicate_email(self):
        # Create another user
        other_password = generate_test_password()
        other_user = User.objects.create_user(
            email='other@example.com',
            username='otheruser',
            first_name='Other',
            last_name='User',
            password=other_password
        )
        
        self.client.force_authenticate(user=self.user)
        
        # Try to update to other user's email
        update_data = {
            'email': 'other@example.com'
        }
        
        response = self.client.patch(self.profile_url, update_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)