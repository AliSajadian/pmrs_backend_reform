"""
Unit tests for accounts serializers.
Tests serialization, deserialization, and validation logic.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from accounts.serializers import (
    LoginSerializer1,
    RegisterSerializer1,
    TokenRefreshSerializer1,
    ChangePasswordSerializer1,
    UserResponseSerializer,
    UserRoleResponseSerializer,
    LoginResponseSerializer,
    TokenRefreshResponseSerializer,
    LogoutResponseSerializer,
    ErrorResponseSerializer
)

User = get_user_model()


class LoginSerializerTest(TestCase):
    """Test LoginSerializer1."""
    
    def test_valid_data(self):
        """Test serializer with valid data."""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        serializer = LoginSerializer1(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['username'], 'testuser')
        self.assertEqual(serializer.validated_data['password'], 'testpass123')
    
    def test_empty_username(self):
        """Test that empty username raises validation error."""
        data = {
            'username': '',
            'password': 'testpass123'
        }
        
        serializer = LoginSerializer1(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
    
    def test_empty_password(self):
        """Test that empty password raises validation error."""
        data = {
            'username': 'testuser',
            'password': ''
        }
        
        serializer = LoginSerializer1(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
    
    def test_missing_username(self):
        """Test that missing username raises validation error."""
        data = {'password': 'testpass123'}
        
        serializer = LoginSerializer1(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
    
    def test_missing_password(self):
        """Test that missing password raises validation error."""
        data = {'username': 'testuser'}
        
        serializer = LoginSerializer1(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
    
    def test_username_whitespace_stripped(self):
        """Test that username whitespace is stripped."""
        data = {
            'username': '  testuser  ',
            'password': 'testpass123'
        }
        
        serializer = LoginSerializer1(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['username'], 'testuser')


class RegisterSerializerTest(TestCase):
    """Test RegisterSerializer1."""
    
    def test_valid_data(self):
        """Test serializer with valid data."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewPass123!@#',
            'password_confirm': 'NewPass123!@#',
            'first_name': 'New',
            'last_name': 'User',
            'personnel_code': 12345
        }
        
        serializer = RegisterSerializer1(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_password_mismatch(self):
        """Test that mismatched passwords raise validation error."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewPass123!@#',
            'password_confirm': 'DifferentPass123!@#',
        }
        
        serializer = RegisterSerializer1(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password_confirm', serializer.errors)
    
    def test_existing_username(self):
        """Test that existing username raises validation error."""
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpass123'
        )
        
        data = {
            'username': 'existinguser',
            'email': 'newemail@example.com',
            'password': 'NewPass123!@#',
            'password_confirm': 'NewPass123!@#',
        }
        
        serializer = RegisterSerializer1(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
    
    def test_existing_email(self):
        """Test that existing email raises validation error."""
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpass123'
        )
        
        data = {
            'username': 'newuser',
            'email': 'existing@example.com',
            'password': 'NewPass123!@#',
            'password_confirm': 'NewPass123!@#',
        }
        
        serializer = RegisterSerializer1(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_weak_password(self):
        """Test that weak password raises validation error."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': '123',  # Too short
            'password_confirm': '123',
        }
        
        serializer = RegisterSerializer1(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
    
    def test_optional_fields(self):
        """Test that optional fields can be omitted."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewPass123!@#',
            'password_confirm': 'NewPass123!@#',
        }
        
        serializer = RegisterSerializer1(data=data)
        self.assertTrue(serializer.is_valid())


class TokenRefreshSerializerTest(TestCase):
    """Test TokenRefreshSerializer1."""
    
    def test_valid_data(self):
        """Test serializer with valid data."""
        data = {'refresh_token': 'valid_token_string'}
        
        serializer = TokenRefreshSerializer1(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['refresh_token'], 'valid_token_string')
    
    def test_empty_token(self):
        """Test that empty token raises validation error."""
        data = {'refresh_token': ''}
        
        serializer = TokenRefreshSerializer1(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('refresh_token', serializer.errors)
    
    def test_missing_token(self):
        """Test that missing token raises validation error."""
        data = {}
        
        serializer = TokenRefreshSerializer1(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('refresh_token', serializer.errors)
    
    def test_token_whitespace_stripped(self):
        """Test that token whitespace is stripped."""
        data = {'refresh_token': '  token_with_spaces  '}
        
        serializer = TokenRefreshSerializer1(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['refresh_token'], 'token_with_spaces')


class ChangePasswordSerializerTest(TestCase):
    """Test ChangePasswordSerializer1."""
    
    def test_valid_data(self):
        """Test serializer with valid data."""
        data = {
            'old_password': 'OldPass123!@#',
            'new_password': 'NewPass123!@#',
            'new_password_confirm': 'NewPass123!@#'
        }
        
        serializer = ChangePasswordSerializer1(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_new_password_mismatch(self):
        """Test that mismatched new passwords raise validation error."""
        data = {
            'old_password': 'OldPass123!@#',
            'new_password': 'NewPass123!@#',
            'new_password_confirm': 'DifferentPass123!@#'
        }
        
        serializer = ChangePasswordSerializer1(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('new_password_confirm', serializer.errors)
    
    def test_same_old_and_new_password(self):
        """Test that same old and new password raises validation error."""
        data = {
            'old_password': 'SamePass123!@#',
            'new_password': 'SamePass123!@#',
            'new_password_confirm': 'SamePass123!@#'
        }
        
        serializer = ChangePasswordSerializer1(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('new_password', serializer.errors)
    
    def test_weak_new_password(self):
        """Test that weak new password raises validation error."""
        data = {
            'old_password': 'OldPass123!@#',
            'new_password': '123',  # Too short
            'new_password_confirm': '123'
        }
        
        serializer = ChangePasswordSerializer1(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('new_password', serializer.errors)


class UserResponseSerializerTest(TestCase):
    """Test UserResponseSerializer."""
    
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
    
    def test_serialization(self):
        """Test user serialization."""
        serializer = UserResponseSerializer(self.user)
        data = serializer.data
        
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['email'], 'test@example.com')
        self.assertEqual(data['first_name'], 'Test')
        self.assertEqual(data['last_name'], 'User')
        self.assertEqual(data['personnel_code'], 12345)
        self.assertIn('full_name', data)
        self.assertEqual(data['full_name'], 'Test User')
    
    def test_full_name_with_empty_names(self):
        """Test full_name returns username when names are empty."""
        user = User.objects.create_user(
            username='noname',
            email='noname@example.com',
            password='testpass123'
        )
        
        serializer = UserResponseSerializer(user)
        data = serializer.data
        
        self.assertEqual(data['full_name'], 'noname')
    
    def test_all_fields_readonly(self):
        """Test that all fields are read-only."""
        serializer = UserResponseSerializer(self.user)
        
        for field_name in serializer.Meta.fields:
            self.assertIn(field_name, serializer.Meta.read_only_fields)


class UserRoleResponseSerializerTest(TestCase):
    """Test UserRoleResponseSerializer."""
    
    def test_serialization(self):
        """Test role serialization."""
        data = {
            'role_id': 1,
            'role': 'Manager',
            'project_id': 100,
            'project_name': 'Test Project',
            'all_projects': False,
            'permissions': ['View Reports', 'Edit Reports']
        }
        
        serializer = UserRoleResponseSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['role'], 'Manager')
        self.assertEqual(len(serializer.validated_data['permissions']), 2)
    
    def test_null_project_fields(self):
        """Test serialization with null project fields."""
        data = {
            'role_id': 1,
            'role': 'Admin',
            'project_id': None,
            'project_name': None,
            'all_projects': True,
            'permissions': ['Full Access']
        }
        
        serializer = UserRoleResponseSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertIsNone(serializer.validated_data['project_id'])
        self.assertTrue(serializer.validated_data['all_projects'])


class LoginResponseSerializerTest(TestCase):
    """Test LoginResponseSerializer."""
    
    def test_serialization(self):
        """Test login response serialization."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        data = {
            'status': 'success',
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': 'testuser',
                'email': 'test@example.com',
                'first_name': '',
                'last_name': '',
                'full_name': 'testuser',
                'personnel_code': None,
                'is_active': True,
                'user_img': None,
                'date_joined': user.date_joined,
                'last_login': None,
            },
            'access_token': 'access_token_string',
            'refresh_token': 'refresh_token_string',
            'token_type': 'Bearer',
            'access_expires_at': 1234567890,
            'refresh_expires_at': 1234567890,
            'roles': [],
            'all_permissions': [],
            'is_admin': False,
            'is_board': False
        }
        
        serializer = LoginResponseSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class TokenRefreshResponseSerializerTest(TestCase):
    """Test TokenRefreshResponseSerializer."""
    
    def test_serialization(self):
        """Test token refresh response serialization."""
        data = {
            'status': 'success',
            'message': 'Token refreshed successfully',
            'access_token': 'new_access_token',
            'refresh_token': 'new_refresh_token',
            'token_type': 'Bearer'
        }
        
        serializer = TokenRefreshResponseSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class LogoutResponseSerializerTest(TestCase):
    """Test LogoutResponseSerializer."""
    
    def test_serialization(self):
        """Test logout response serialization."""
        data = {
            'status': 'success',
            'message': 'Logout successful'
        }
        
        serializer = LogoutResponseSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class ErrorResponseSerializerTest(TestCase):
    """Test ErrorResponseSerializer."""
    
    def test_serialization_with_errors(self):
        """Test error response serialization with error details."""
        data = {
            'status': 'error',
            'message': 'Validation failed',
            'errors': {
                'username': ['This field is required'],
                'password': ['This field is required']
            }
        }
        
        serializer = ErrorResponseSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_serialization_without_errors(self):
        """Test error response serialization without error details."""
        data = {
            'status': 'error',
            'message': 'Something went wrong'
        }
        
        serializer = ErrorResponseSerializer(data=data)
        self.assertTrue(serializer.is_valid())


# Run tests with: python manage.py test accounts.tests.test_serializers