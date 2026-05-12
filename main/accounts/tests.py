"""
Comprehensive tests for the accounts application with JWT authentication.

This module contains tests for:
- AuthService: Login, logout, token refresh
- TokenService: Token generation, storage, validation
- UserService: User creation, updates, password changes
- API endpoints: Integration tests
- Permissions: Role and permission checks
- Redis: Token storage and revocation
"""
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.core.cache import caches
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from unittest.mock import patch, MagicMock

from accounts.models import Role, Permission, UserRole, RolePermission
from accounts.services import (
    AuthService,
    TokenService,
    UserService,
    PermissionService
)
from contracts.models import Contract

User = get_user_model()


class TokenServiceTestCase(TransactionTestCase):
    """Tests for TokenService"""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User'
        )
        
        # Create role and permission
        self.role = Role.objects.create(
            role='Test Role',
            description='Test role for testing'
        )
        self.permission = Permission.objects.create(
            permission='Test Permission R/W',
            description='Test permission'
        )
        RolePermission.objects.create(
            roleid=self.role,
            permissionid=self.permission
        )
    
    def tearDown(self):
        """Clean up test data."""
        # Clear Redis cache
        try:
            cache = caches['tokens']
            cache.clear()
        except Exception:
            pass
    
    def test_generate_tokens_for_user(self):
        """Test token generation for a user."""
        access_token, refresh_token, token_data = TokenService.generate_tokens_for_user(
            user=self.user,
            device_info='Test Device',
            ip_address='127.0.0.1'
        )
        
        self.assertIsNotNone(access_token)
        self.assertIsNotNone(refresh_token)
        self.assertEqual(token_data['username'], 'testuser')
        self.assertEqual(token_data['email'], 'test@example.com')
        self.assertEqual(token_data['token_type'], 'Bearer')
        self.assertIn('roles', token_data)
        self.assertIn('all_permissions', token_data)
    
    def test_generate_tokens_with_roles(self):
        """Test token generation includes user roles and permissions."""
        # Assign role to user
        user_role = UserRole.objects.create(
            userid=self.user,
            roleid=self.role,
            projectid=None,
            all_projects=True
        )
        
        access_token, refresh_token, token_data = TokenService.generate_tokens_for_user(
            user=self.user
        )
        
        self.assertEqual(len(token_data['roles']), 1)
        self.assertEqual(token_data['roles'][0]['role'], 'Test Role')
        self.assertIn('Test Permission R/W', token_data['all_permissions'])
    
    def test_refresh_access_token(self):
        """Test refreshing access token."""
        # Generate initial tokens
        _, refresh_token, _ = TokenService.generate_tokens_for_user(self.user)
        
        # Refresh tokens
        new_access, new_refresh = TokenService.refresh_access_token(refresh_token)
        
        self.assertIsNotNone(new_access)
        self.assertIsNotNone(new_refresh)
        self.assertNotEqual(refresh_token, new_refresh)
    
    def test_revoke_user_token(self):
        """Test revoking a specific user token."""
        _, refresh_token, _ = TokenService.generate_tokens_for_user(self.user)
        
        # Get token JTI
        refresh = RefreshToken(refresh_token)
        token_jti = str(refresh['jti'])
        
        # Revoke token
        success = TokenService.revoke_user_token(self.user.id, token_jti)
        self.assertTrue(success)
        
        # Verify token is invalid
        is_valid = TokenService._is_token_valid(self.user.id, token_jti)
        self.assertFalse(is_valid)
    
    def test_revoke_all_user_tokens(self):
        """Test revoking all tokens for a user."""
        # Generate multiple tokens
        for _ in range(3):
            TokenService.generate_tokens_for_user(self.user)
        
        # Revoke all tokens
        count = TokenService.revoke_all_user_tokens(self.user.id)
        self.assertEqual(count, 3)


class AuthServiceTestCase(TransactionTestCase):
    """Tests for AuthService"""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='authuser',
            email='auth@example.com',
            password='AuthPass123!',
            first_name='Auth',
            last_name='User',
            is_active=True
        )
        self.inactive_user = User.objects.create_user(
            username='inactive',
            email='inactive@example.com',
            password='InactivePass123!',
            is_active=False
        )
    
    def tearDown(self):
        """Clean up test data."""
        try:
            cache = caches['tokens']
            cache.clear()
        except Exception:
            pass
    
    def test_authenticate_user_success(self):
        """Test successful user authentication."""
        user, access_token, refresh_token, token_data = AuthService.authenticate_user(
            username='authuser',
            password='AuthPass123!'
        )
        
        self.assertEqual(user.username, 'authuser')
        self.assertIsNotNone(access_token)
        self.assertIsNotNone(refresh_token)
    
    def test_authenticate_user_invalid_username(self):
        """Test authentication with invalid username."""
        with self.assertRaises(ValidationError) as context:
            AuthService.authenticate_user(
                username='nonexistent',
                password='anypassword'
            )
        self.assertIn('Invalid username or password', str(context.exception))
    
    def test_authenticate_user_invalid_password(self):
        """Test authentication with invalid password."""
        with self.assertRaises(ValidationError) as context:
            AuthService.authenticate_user(
                username='authuser',
                password='wrongpassword'
            )
        self.assertIn('Invalid username or password', str(context.exception))
    
    def test_authenticate_inactive_user(self):
        """Test authentication with inactive user."""
        with self.assertRaises(ValidationError) as context:
            AuthService.authenticate_user(
                username='inactive',
                password='InactivePass123!'
            )
        self.assertIn('disabled', str(context.exception))
    
    def test_logout_user_single_device(self):
        """Test logging out from a single device."""
        _, access_token, refresh_token, _ = AuthService.authenticate_user(
            username='authuser',
            password='AuthPass123!'
        )
        
        success = AuthService.logout_user(self.user, refresh_token=refresh_token)
        self.assertTrue(success)
    
    def test_logout_user_all_devices(self):
        """Test logging out from all devices."""
        # Generate multiple sessions
        for _ in range(2):
            AuthService.authenticate_user(
                username='authuser',
                password='AuthPass123!'
            )
        
        success = AuthService.logout_user(self.user, logout_all=True)
        self.assertTrue(success)
    
    def test_refresh_tokens_success(self):
        """Test successful token refresh."""
        _, _, refresh_token, _ = AuthService.authenticate_user(
            username='authuser',
            password='AuthPass123!'
        )
        
        new_access, new_refresh = AuthService.refresh_tokens(refresh_token)
        self.assertIsNotNone(new_access)
        self.assertIsNotNone(new_refresh)
    
    def test_refresh_tokens_invalid_token(self):
        """Test token refresh with invalid token."""
        with self.assertRaises(ValidationError):
            AuthService.refresh_tokens('invalid_token')


class UserServiceTestCase(TransactionTestCase):
    """Tests for UserService"""
    
    def test_create_user_success(self):
        """Test successful user creation."""
        user = UserService.create_user(
            username='newuser',
            email='newuser@example.com',
            password='NewPass123!',
            first_name='New',
            last_name='User',
            personnel_code=1234
        )
        
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertTrue(user.check_password('NewPass123!'))
        self.assertTrue(user.is_active)
    
    def test_create_user_duplicate_username(self):
        """Test user creation with duplicate username."""
        UserService.create_user(
            username='duplicate',
            email='first@example.com',
            password='Pass123!'
        )
        
        with self.assertRaises(ValidationError) as context:
            UserService.create_user(
                username='duplicate',
                email='second@example.com',
                password='Pass123!'
            )
        self.assertIn('Username already exists', str(context.exception))
    
    def test_create_user_duplicate_email(self):
        """Test user creation with duplicate email."""
        UserService.create_user(
            username='user1',
            email='same@example.com',
            password='Pass123!'
        )
        
        with self.assertRaises(ValidationError) as context:
            UserService.create_user(
                username='user2',
                email='same@example.com',
                password='Pass123!'
            )
        self.assertIn('Email already exists', str(context.exception))
    
    def test_update_user(self):
        """Test updating user information."""
        user = UserService.create_user(
            username='updateuser',
            email='update@example.com',
            password='Pass123!'
        )
        
        updated_user = UserService.update_user(
            user_id=user.id,
            first_name='Updated',
            last_name='Name',
            email='newemail@example.com'
        )
        
        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertEqual(updated_user.last_name, 'Name')
        self.assertEqual(updated_user.email, 'newemail@example.com')
    
    def test_change_password_success(self):
        """Test successful password change."""
        user = UserService.create_user(
            username='passuser',
            email='passuser@example.com',
            password='OldPass123!'
        )
        
        success = UserService.change_password(
            user_id=user.id,
            old_password='OldPass123!',
            new_password='NewPass456!'
        )
        
        self.assertTrue(success)
        user.refresh_from_db()
        self.assertTrue(user.check_password('NewPass456!'))
    
    def test_change_password_wrong_old_password(self):
        """Test password change with wrong old password."""
        user = UserService.create_user(
            username='passuser2',
            email='passuser2@example.com',
            password='OldPass123!'
        )
        
        with self.assertRaises(ValidationError) as context:
            UserService.change_password(
                user_id=user.id,
                old_password='WrongPass!',
                new_password='NewPass456!'
            )
        self.assertIn('incorrect', str(context.exception))
    
    def test_change_password_same_as_old(self):
        """Test password change with same password."""
        user = UserService.create_user(
            username='passuser3',
            email='passuser3@example.com',
            password='OldPass123!'
        )
        
        with self.assertRaises(ValidationError) as context:
            UserService.change_password(
                user_id=user.id,
                old_password='OldPass123!',
                new_password='OldPass123!'
            )
        self.assertIn('different', str(context.exception))
    
    def test_deactivate_user(self):
        """Test user deactivation."""
        user = UserService.create_user(
            username='deactiveuser',
            email='deactive@example.com',
            password='Pass123!'
        )
        
        success = UserService.deactivate_user(user.id)
        self.assertTrue(success)
        
        user.refresh_from_db()
        self.assertFalse(user.is_active)


class PermissionServiceTestCase(TransactionTestCase):
    """Tests for PermissionService"""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='permuser',
            email='perm@example.com',
            password='Pass123!'
        )
        
        self.role = Role.objects.create(role='Admin Role')
        self.permission = Permission.objects.create(permission='Budget R/W')
        RolePermission.objects.create(
            roleid=self.role,
            permissionid=self.permission
        )
    
    def test_get_user_roles_no_roles(self):
        """Test getting roles for user with no roles."""
        result = PermissionService.get_user_roles_and_permissions(self.user)
        
        self.assertEqual(len(result['roles']), 0)
        self.assertFalse(result['is_admin'])
        self.assertFalse(result['is_board'])
    
    def test_get_user_roles_with_roles(self):
        """Test getting roles for user with roles."""
        UserRole.objects.create(
            userid=self.user,
            roleid=self.role,
            all_projects=True
        )
        
        result = PermissionService.get_user_roles_and_permissions(self.user)
        
        self.assertEqual(len(result['roles']), 1)
        self.assertTrue(result['is_admin'])
        self.assertIn('Budget R/W', result['all_permissions'])
    
    def test_check_user_permission_has_permission(self):
        """Test checking user permission when user has it."""
        UserRole.objects.create(
            userid=self.user,
            roleid=self.role,
            all_projects=True
        )
        
        has_perm = PermissionService.check_user_permission(
            self.user,
            'Budget R/W'
        )
        self.assertTrue(has_perm)
    
    def test_check_user_permission_no_permission(self):
        """Test checking user permission when user doesn't have it."""
        has_perm = PermissionService.check_user_permission(
            self.user,
            'Budget R/W'
        )
        self.assertFalse(has_perm)


class AuthenticationAPITestCase(APITestCase):
    """Integration tests for authentication API endpoints"""
    
    def setUp(self):
        """Set up test client and data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@example.com',
            password='ApiPass123!',
            first_name='API',
            last_name='User',
            is_active=True
        )
    
    def tearDown(self):
        """Clean up test data."""
        try:
            cache = caches['tokens']
            cache.clear()
        except Exception:
            pass
    
    def test_login_endpoint_success(self):
        """Test successful login via API."""
        response = self.client.post('/api/auth/login', {
            'username': 'apiuser',
            'password': 'ApiPass123!'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
        self.assertIn('user', response.data)
    
    def test_login_endpoint_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = self.client.post('/api/auth/login', {
            'username': 'apiuser',
            'password': 'wrongpassword'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['status'], 'error')
    
    def test_login_endpoint_missing_fields(self):
        """Test login with missing fields."""
        response = self.client.post('/api/auth/login', {
            'username': 'apiuser'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_logout_endpoint(self):
        """Test logout via API."""
        # Login first
        login_response = self.client.post('/api/auth/login', {
            'username': 'apiuser',
            'password': 'ApiPass123!'
        }, format='json')
        
        access_token = login_response.data['access_token']
        refresh_token = login_response.data['refresh_token']
        
        # Logout
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        logout_response = self.client.post('/api/auth/logout', {
            'refresh_token': refresh_token
        }, format='json')
        
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        self.assertEqual(logout_response.data['status'], 'success')
    
    def test_refresh_endpoint(self):
        """Test token refresh via API."""
        # Login first
        login_response = self.client.post('/api/auth/login', {
            'username': 'apiuser',
            'password': 'ApiPass123!'
        }, format='json')
        
        refresh_token = login_response.data['refresh_token']
        
        # Refresh tokens
        refresh_response = self.client.post('/api/auth/refresh', {
            'refresh_token': refresh_token
        }, format='json')
        
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertEqual(refresh_response.data['status'], 'success')
        self.assertIn('access_token', refresh_response.data)
        self.assertIn('refresh_token', refresh_response.data)
    
    def test_register_endpoint(self):
        """Test user registration via API."""
        response = self.client.post('/api/auth/register', {
            'username': 'newapi',
            'email': 'newapi@example.com',
            'password': 'NewApiPass123!',
            'password_confirm': 'NewApiPass123!',
            'first_name': 'New',
            'last_name': 'API'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('access_token', response.data)
        self.assertIn('user', response.data)
    
    def test_register_endpoint_password_mismatch(self):
        """Test registration with password mismatch."""
        response = self.client.post('/api/auth/register', {
            'username': 'newapi2',
            'email': 'newapi2@example.com',
            'password': 'Pass123!',
            'password_confirm': 'DifferentPass123!'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_change_password_endpoint(self):
        """Test password change via API."""
        # Login first
        login_response = self.client.post('/api/auth/login', {
            'username': 'apiuser',
            'password': 'ApiPass123!'
        }, format='json')
        
        access_token = login_response.data['access_token']
        
        # Change password
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.put('/api/auth/changePassword', {
            'old_password': 'ApiPass123!',
            'new_password': 'NewApiPass456!',
            'new_password_confirm': 'NewApiPass456!'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
    
    def test_profile_endpoint(self):
        """Test getting user profile via API."""
        # Login first
        login_response = self.client.post('/api/auth/login', {
            'username': 'apiuser',
            'password': 'ApiPass123!'
        }, format='json')
        
        access_token = login_response.data['access_token']
        
        # Get profile
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get('/api/auth/profile')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['data']['username'], 'apiuser')


class RedisIntegrationTestCase(TransactionTestCase):
    """Tests for Redis integration"""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='redisuser',
            email='redis@example.com',
            password='Pass123!'
        )
        try:
            self.cache = caches['tokens']
            self.cache.clear()
        except Exception:
            self.skipTest("Redis cache not available")
    
    def tearDown(self):
        """Clean up Redis."""
        try:
            self.cache.clear()
        except Exception:
            pass
    
    def test_token_stored_in_redis(self):
        """Test that tokens are stored in Redis."""
        _, refresh_token, _ = TokenService.generate_tokens_for_user(self.user)
        
        refresh = RefreshToken(refresh_token)
        token_jti = str(refresh['jti'])
        
        # Check if token is in Redis
        token_key = f"refresh_token:{self.user.id}:{token_jti}"
        token_data = self.cache.get(token_key)
        
        self.assertIsNotNone(token_data)
        self.assertEqual(token_data['user_id'], self.user.id)
    
    def test_multiple_tokens_per_user(self):
        """Test storing multiple tokens for one user."""
        tokens = []
        for _ in range(3):
            _, refresh_token, _ = TokenService.generate_tokens_for_user(self.user)
            tokens.append(refresh_token)
        
        # Check user tokens set
        user_tokens_key = f"user_tokens:{self.user.id}"
        user_tokens = self.cache.get(user_tokens_key)
        
        self.assertEqual(len(user_tokens), 3)
    
    def test_token_expiration(self):
        """Test that tokens have expiration set in Redis."""
        _, refresh_token, _ = TokenService.generate_tokens_for_user(self.user)
        
        refresh = RefreshToken(refresh_token)
        token_jti = str(refresh['jti'])
        token_key = f"refresh_token:{self.user.id}:{token_jti}"
        
        # Check TTL (should be around 7 days = 604800 seconds)
        ttl = self.cache.ttl(token_key)
        self.assertGreater(ttl, 0)
        self.assertLessEqual(ttl, 60 * 60 * 24 * 7)  # 7 days
