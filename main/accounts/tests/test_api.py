"""
Integration tests for accounts API views.
Tests HTTP request/response flow, authentication, and serialization.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from django.core.cache import caches

from accounts.services import TokenService

User = get_user_model()


class LoginAPIViewTest(APITestCase):
    """Test login API endpoint."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.url = '/api/auth/login/'  # Adjust to your actual URL
        
        # Clear Redis cache
        cache = caches[TokenService.REDIS_CACHE_ALIAS]
        cache.clear()
    
    def tearDown(self):
        """Clean up after each test."""
        cache = caches[TokenService.REDIS_CACHE_ALIAS]
        cache.clear()
    
    def test_login_success(self):
        """Test successful login."""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
    
    def test_login_with_wrong_password(self):
        """Test login with wrong password."""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['status'], 'error')
    
    def test_login_with_nonexistent_user(self):
        """Test login with non-existent user."""
        data = {
            'username': 'nonexistent',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['status'], 'error')
    
    def test_login_with_inactive_user(self):
        """Test login with inactive user."""
        self.user.is_active = False
        self.user.save()
        
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_with_empty_username(self):
        """Test login with empty username."""
        data = {
            'username': '',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data)
    
    def test_login_with_missing_fields(self):
        """Test login with missing required fields."""
        data = {'username': 'testuser'}
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_response_contains_roles_and_permissions(self):
        """Test that login response contains roles and permissions."""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertIn('roles', response.data)
        self.assertIn('all_permissions', response.data)
        self.assertIn('is_admin', response.data)
        self.assertIn('is_board', response.data)


class LogoutAPIViewTest(APITestCase):
    """Test logout API endpoint."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.url = '/api/auth/logout/'  # Adjust to your actual URL
        
        # Clear Redis cache
        cache = caches[TokenService.REDIS_CACHE_ALIAS]
        cache.clear()
        
        # Generate tokens
        _, self.refresh_token, _ = TokenService.generate_tokens_for_user(self.user)
    
    def tearDown(self):
        """Clean up after each test."""
        cache = caches[TokenService.REDIS_CACHE_ALIAS]
        cache.clear()
    
    def test_logout_single_device(self):
        """Test logout from single device."""
        data = {
            'refresh_token': self.refresh_token,
            'logout_all': False
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
    
    def test_logout_all_devices(self):
        """Test logout from all devices."""
        data = {
            'logout_all': True
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('all devices', response.data['message'])
    
    def test_logout_requires_authentication(self):
        """Test that logout requires authentication."""
        self.client.force_authenticate(user=None)
        
        data = {'logout_all': True}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenRefreshAPIViewTest(APITestCase):
    """Test token refresh API endpoint."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.url = '/api/auth/refresh/'  # Adjust to your actual URL
        
        # Clear Redis cache
        cache = caches[TokenService.REDIS_CACHE_ALIAS]
        cache.clear()
        
        # Generate tokens
        _, self.refresh_token, _ = TokenService.generate_tokens_for_user(self.user)
    
    def tearDown(self):
        """Clean up after each test."""
        cache = caches[TokenService.REDIS_CACHE_ALIAS]
        cache.clear()
    
    def test_refresh_token_success(self):
        """Test successful token refresh."""
        data = {'refresh_token': self.refresh_token}
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
    
    def test_refresh_with_invalid_token(self):
        """Test token refresh with invalid token."""
        data = {'refresh_token': 'invalid_token'}
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_refresh_with_empty_token(self):
        """Test token refresh with empty token."""
        data = {'refresh_token': ''}
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data)


class RegisterAPIViewTest(APITestCase):
    """Test registration API endpoint."""
    
    def setUp(self):
        """Set up test data."""
        self.url = '/api/auth/register/'  # Adjust to your actual URL
        
        # Clear Redis cache
        cache = caches[TokenService.REDIS_CACHE_ALIAS]
        cache.clear()
    
    def tearDown(self):
        """Clean up after each test."""
        cache = caches[TokenService.REDIS_CACHE_ALIAS]
        cache.clear()
    
    def test_register_success(self):
        """Test successful user registration."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewPass123!@#',
            'password_confirm': 'NewPass123!@#',
            'first_name': 'New',
            'last_name': 'User',
            'personnel_code': 12345
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('user', response.data)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
    
    def test_register_with_existing_username(self):
        """Test registration with existing username."""
        User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='testpass123'
        )
        
        data = {
            'username': 'existing',
            'email': 'newemail@example.com',
            'password': 'NewPass123!@#',
            'password_confirm': 'NewPass123!@#'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data['errors'])
    
    def test_register_with_password_mismatch(self):
        """Test registration with mismatched passwords."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewPass123!@#',
            'password_confirm': 'DifferentPass123!@#'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data['errors'])
    
    def test_register_with_weak_password(self):
        """Test registration with weak password."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': '123',
            'password_confirm': '123'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ChangePasswordAPIViewTest(APITestCase):
    """Test change password API endpoint."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='OldPass123!@#'
        )
        self.client.force_authenticate(user=self.user)
        self.url = '/api/auth/changePassword/'  # Adjust to your actual URL
    
    def test_change_password_success(self):
        """Test successful password change."""
        data = {
            'old_password': 'OldPass123!@#',
            'new_password': 'NewPass123!@#',
            'new_password_confirm': 'NewPass123!@#'
        }
        
        response = self.client.put(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        
        # Verify password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPass123!@#'))
    
    def test_change_password_with_wrong_old_password(self):
        """Test password change with wrong old password."""
        data = {
            'old_password': 'WrongPassword',
            'new_password': 'NewPass123!@#',
            'new_password_confirm': 'NewPass123!@#'
        }
        
        response = self.client.put(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_change_password_with_mismatch(self):
        """Test password change with mismatched new passwords."""
        data = {
            'old_password': 'OldPass123!@#',
            'new_password': 'NewPass123!@#',
            'new_password_confirm': 'DifferentPass123!@#'
        }
        
        response = self.client.put(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('new_password_confirm', response.data['errors'])
    
    def test_change_password_requires_authentication(self):
        """Test that password change requires authentication."""
        self.client.force_authenticate(user=None)
        
        data = {
            'old_password': 'OldPass123!@#',
            'new_password': 'NewPass123!@#',
            'new_password_confirm': 'NewPass123!@#'
        }
        
        response = self.client.put(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserProfileAPIViewTest(APITestCase):
    """Test user profile API endpoint."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            personnel_code=12345
        )
        self.client.force_authenticate(user=self.user)
        self.url = '/api/auth/profile/'  # Adjust to your actual URL
    
    def test_get_profile_success(self):
        """Test getting user profile."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['username'], 'testuser')
        self.assertEqual(response.data['data']['email'], 'test@example.com')
        self.assertEqual(response.data['data']['personnel_code'], 12345)
    
    def test_get_profile_requires_authentication(self):
        """Test that getting profile requires authentication."""
        self.client.force_authenticate(user=None)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_profile_contains_full_name(self):
        """Test that profile response contains full_name field."""
        response = self.client.get(self.url)
        
        self.assertIn('full_name', response.data['data'])
        self.assertEqual(response.data['data']['full_name'], 'Test User')


class APIErrorHandlingTest(APITestCase):
    """Test API error handling."""
    
    def test_invalid_json_returns_400(self):
        """Test that invalid JSON returns 400 error."""
        url = '/api/auth/login/'
        
        response = self.client.post(
            url,
            data='invalid json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_method_not_allowed_returns_405(self):
        """Test that wrong HTTP method returns 405."""
        url = '/api/auth/login/'
        
        response = self.client.get(url)  # Should be POST
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


# Run tests with: python manage.py test accounts.tests.test_api