"""
Unit tests for accounts services.
Tests business logic without HTTP overhead.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.cache import caches
from unittest.mock import patch, MagicMock
from rest_framework_simplejwt.exceptions import TokenError

from accounts.services import (
    PermissionService,
    TokenService,
    AuthService,
    UserService
)
from accounts.models import Role, Permission, UserRole, RolePermission
from contracts.models import Contract

User = get_user_model()


class PermissionServiceTest(TestCase):
    """Test PermissionService business logic."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        
        self.role = Role.objects.create(role='Manager')
        self.permission = Permission.objects.create(permission='View Reports')
        
        RolePermission.objects.create(
            roleid=self.role,
            permissionid=self.permission
        )
    
    def test_get_user_roles_and_permissions(self):
        """Test getting user roles and permissions."""
        UserRole.objects.create(
            userid=self.user,
            projectid=self.contract,
            roleid=self.role
        )
        
        result = PermissionService.get_user_roles_and_permissions(self.user)
        
        self.assertTrue(result['has_roles'])
        self.assertEqual(len(result['roles']), 1)
        self.assertIn('View Reports', result['all_permissions'])
    
    def test_user_with_admin_role(self):
        """Test identifying admin users."""
        admin_role = Role.objects.create(role='System Admin')
        UserRole.objects.create(
            userid=self.user,
            roleid=admin_role
        )
        
        result = PermissionService.get_user_roles_and_permissions(self.user)
        
        self.assertTrue(result['is_admin'])
    
    def test_user_with_board_role(self):
        """Test identifying board members."""
        board_role = Role.objects.create(role='Board Member')
        UserRole.objects.create(
            userid=self.user,
            roleid=board_role
        )
        
        result = PermissionService.get_user_roles_and_permissions(self.user)
        
        self.assertTrue(result['is_board'])
    
    def test_user_with_all_projects_flag(self):
        """Test user with all_projects flag."""
        UserRole.objects.create(
            userid=self.user,
            roleid=self.role,
            all_projects=True
        )
        
        result = PermissionService.get_user_roles_and_permissions(self.user)
        
        self.assertTrue(result['roles'][0]['all_projects'])
        self.assertIsNone(result['roles'][0]['project_id'])
    
    def test_check_user_permission_success(self):
        """Test checking user permission returns True when user has permission."""
        UserRole.objects.create(
            userid=self.user,
            projectid=self.contract,
            roleid=self.role
        )
        
        has_permission = PermissionService.check_user_permission(
            self.user,
            'View Reports',
            self.contract.contractid
        )
        
        self.assertTrue(has_permission)
    
    def test_check_user_permission_failure(self):
        """Test checking user permission returns False when user lacks permission."""
        UserRole.objects.create(
            userid=self.user,
            projectid=self.contract,
            roleid=self.role
        )
        
        has_permission = PermissionService.check_user_permission(
            self.user,
            'Delete Reports',
            self.contract.contractid
        )
        
        self.assertFalse(has_permission)
    
    def test_check_user_permission_with_all_projects(self):
        """Test permission check with all_projects flag."""
        UserRole.objects.create(
            userid=self.user,
            roleid=self.role,
            all_projects=True
        )
        
        has_permission = PermissionService.check_user_permission(
            self.user,
            'View Reports',
            999  # Different project
        )
        
        self.assertTrue(has_permission)


class TokenServiceTest(TestCase):
    """Test TokenService business logic."""
    
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
        
        # Clear Redis cache before each test
        cache = caches[TokenService.REDIS_CACHE_ALIAS]
        cache.clear()
    
    def tearDown(self):
        """Clean up after each test."""
        cache = caches[TokenService.REDIS_CACHE_ALIAS]
        cache.clear()
    
    def test_generate_tokens_for_user(self):
        """Test generating tokens for user."""
        access_token, refresh_token, token_data = TokenService.generate_tokens_for_user(
            user=self.user,
            device_info='Test Device',
            ip_address='127.0.0.1'
        )
        
        self.assertIsNotNone(access_token)
        self.assertIsNotNone(refresh_token)
        self.assertEqual(token_data['user_id'], self.user.id)
        self.assertEqual(token_data['username'], 'testuser')
        self.assertEqual(token_data['token_type'], 'Bearer')
    
    def test_generated_tokens_contain_custom_claims(self):
        """Test that generated tokens contain custom claims."""
        _, _, token_data = TokenService.generate_tokens_for_user(self.user)
        
        self.assertIn('user_id', token_data)
        self.assertIn('username', token_data)
        self.assertIn('email', token_data)
        self.assertIn('full_name', token_data)
        self.assertIn('personnel_code', token_data)
        self.assertIn('roles', token_data)
        self.assertIn('all_permissions', token_data)
        self.assertIn('is_admin', token_data)
        self.assertIn('is_board', token_data)
    
    @patch('accounts.services.PermissionService.get_user_roles_and_permissions')
    def test_tokens_include_roles_and_permissions(self, mock_get_roles):
        """Test that tokens include user roles and permissions."""
        mock_get_roles.return_value = {
            'roles': [{'role': 'Manager', 'permissions': ['View Reports']}],
            'all_permissions': ['View Reports'],
            'is_admin': False,
            'is_board': False,
            'has_roles': True
        }
        
        _, _, token_data = TokenService.generate_tokens_for_user(self.user)
        
        self.assertEqual(len(token_data['roles']), 1)
        self.assertIn('View Reports', token_data['all_permissions'])
    
    def test_refresh_access_token(self):
        """Test refreshing access token."""
        # Generate initial tokens
        _, refresh_token, _ = TokenService.generate_tokens_for_user(self.user)
        
        # Refresh tokens
        new_access, new_refresh = TokenService.refresh_access_token(refresh_token)
        
        self.assertIsNotNone(new_access)
        self.assertIsNotNone(new_refresh)
        self.assertNotEqual(refresh_token, new_refresh)
    
    def test_refresh_with_invalid_token_raises_error(self):
        """Test that refreshing with invalid token raises error."""
        with self.assertRaises(TokenError):
            TokenService.refresh_access_token('invalid_token')
    
    def test_revoke_user_token(self):
        """Test revoking a specific user token."""
        # Generate tokens
        _, refresh_token, _ = TokenService.generate_tokens_for_user(self.user)
        
        # Extract JTI from token
        from rest_framework_simplejwt.tokens import RefreshToken
        token = RefreshToken(refresh_token)
        token_jti = str(token['jti'])
        
        # Revoke token
        success = TokenService.revoke_user_token(self.user.id, token_jti)
        self.assertTrue(success)
        
        # Try to refresh with revoked token should fail
        with self.assertRaises(TokenError):
            TokenService.refresh_access_token(refresh_token)
    
    def test_revoke_all_user_tokens(self):
        """Test revoking all tokens for a user."""
        # Generate multiple tokens
        TokenService.generate_tokens_for_user(self.user)
        TokenService.generate_tokens_for_user(self.user)
        TokenService.generate_tokens_for_user(self.user)
        
        # Revoke all
        count = TokenService.revoke_all_user_tokens(self.user.id)
        
        self.assertEqual(count, 3)


class AuthServiceTest(TestCase):
    """Test AuthService business logic."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Clear Redis cache
        cache = caches[TokenService.REDIS_CACHE_ALIAS]
        cache.clear()
    
    def tearDown(self):
        """Clean up after each test."""
        cache = caches[TokenService.REDIS_CACHE_ALIAS]
        cache.clear()
    
    def test_authenticate_user_success(self):
        """Test successful user authentication."""
        user, access, refresh, token_data = AuthService.authenticate_user(
            username='testuser',
            password='testpass123',
            device_info='Test Device',
            ip_address='127.0.0.1'
        )
        
        self.assertEqual(user, self.user)
        self.assertIsNotNone(access)
        self.assertIsNotNone(refresh)
        self.assertIn('roles', token_data)
    
    def test_authenticate_with_wrong_password(self):
        """Test authentication with wrong password raises error."""
        with self.assertRaises(ValidationError) as context:
            AuthService.authenticate_user(
                username='testuser',
                password='wrongpassword'
            )
        
        self.assertIn('Invalid username or password', str(context.exception))
    
    def test_authenticate_with_nonexistent_user(self):
        """Test authentication with non-existent user raises error."""
        with self.assertRaises(ValidationError) as context:
            AuthService.authenticate_user(
                username='nonexistent',
                password='testpass123'
            )
        
        self.assertIn('Invalid username or password', str(context.exception))
    
    def test_authenticate_inactive_user(self):
        """Test authentication with inactive user raises error."""
        self.user.is_active = False
        self.user.save()
        
        with self.assertRaises(ValidationError) as context:
            AuthService.authenticate_user(
                username='testuser',
                password='testpass123'
            )
        
        self.assertIn('User account is disabled', str(context.exception))
    
    def test_logout_user_single_device(self):
        """Test logging out from single device."""
        # Login to get tokens
        _, _, refresh, _ = AuthService.authenticate_user(
            username='testuser',
            password='testpass123'
        )
        
        # Logout
        success = AuthService.logout_user(
            user=self.user,
            refresh_token=refresh,
            logout_all=False
        )
        
        self.assertTrue(success)
    
    def test_logout_user_all_devices(self):
        """Test logging out from all devices."""
        # Login multiple times
        AuthService.authenticate_user('testuser', 'testpass123')
        AuthService.authenticate_user('testuser', 'testpass123')
        
        # Logout from all devices
        success = AuthService.logout_user(
            user=self.user,
            logout_all=True
        )
        
        self.assertTrue(success)
    
    def test_refresh_tokens_success(self):
        """Test successful token refresh."""
        # Get initial tokens
        _, _, refresh, _ = AuthService.authenticate_user(
            username='testuser',
            password='testpass123'
        )
        
        # Refresh
        new_access, new_refresh = AuthService.refresh_tokens(refresh)
        
        self.assertIsNotNone(new_access)
        self.assertIsNotNone(new_refresh)
    
    def test_refresh_tokens_with_invalid_token(self):
        """Test token refresh with invalid token raises error."""
        with self.assertRaises(ValidationError):
            AuthService.refresh_tokens('invalid_token')


class UserServiceTest(TestCase):
    """Test UserService business logic."""
    
    def setUp(self):
        """Set up test data."""
        # Clear Redis cache
        cache = caches[TokenService.REDIS_CACHE_ALIAS]
        cache.clear()
    
    def test_create_user_success(self):
        """Test successful user creation."""
        user = UserService.create_user(
            username='newuser',
            email='newuser@example.com',
            password='NewPass123!@#',
            first_name='New',
            last_name='User',
            personnel_code=12345,
            is_active=True
        )
        
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.personnel_code, 12345)
        self.assertTrue(user.is_active)
        self.assertTrue(user.check_password('NewPass123!@#'))
    
    def test_create_user_with_existing_username(self):
        """Test creating user with existing username raises error."""
        User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='testpass123'
        )
        
        with self.assertRaises(ValidationError) as context:
            UserService.create_user(
                username='existing',
                email='newemail@example.com',
                password='testpass123'
            )
        
        self.assertIn('Username already exists', str(context.exception))
    
    def test_create_user_with_existing_email(self):
        """Test creating user with existing email raises error."""
        User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='testpass123'
        )
        
        with self.assertRaises(ValidationError) as context:
            UserService.create_user(
                username='newuser',
                email='existing@example.com',
                password='testpass123'
            )
        
        self.assertIn('Email already exists', str(context.exception))
    
    def test_update_user_success(self):
        """Test successful user update."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        updated_user = UserService.update_user(
            user_id=user.id,
            first_name='Updated',
            last_name='Name',
            personnel_code=99999
        )
        
        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertEqual(updated_user.last_name, 'Name')
        self.assertEqual(updated_user.personnel_code, 99999)
    
    def test_update_nonexistent_user(self):
        """Test updating non-existent user raises error."""
        with self.assertRaises(ValidationError):
            UserService.update_user(
                user_id=99999,
                first_name='Test'
            )
    
    def test_change_password_success(self):
        """Test successful password change."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='OldPass123!@#'
        )
        
        success = UserService.change_password(
            user_id=user.id,
            old_password='OldPass123!@#',
            new_password='NewPass123!@#'
        )
        
        self.assertTrue(success)
        
        # Verify new password works
        user.refresh_from_db()
        self.assertTrue(user.check_password('NewPass123!@#'))
    
    def test_change_password_with_wrong_old_password(self):
        """Test password change with wrong old password raises error."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='OldPass123!@#'
        )
        
        with self.assertRaises(ValidationError) as context:
            UserService.change_password(
                user_id=user.id,
                old_password='WrongPassword',
                new_password='NewPass123!@#'
            )
        
        self.assertIn('Current password is incorrect', str(context.exception))
    
    def test_change_password_to_same_password(self):
        """Test changing password to same password raises error."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SamePass123!@#'
        )
        
        with self.assertRaises(ValidationError) as context:
            UserService.change_password(
                user_id=user.id,
                old_password='SamePass123!@#',
                new_password='SamePass123!@#'
            )
        
        self.assertIn('New password must be different', str(context.exception))
    
    def test_deactivate_user_success(self):
        """Test successful user deactivation."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        success = UserService.deactivate_user(user.id)
        
        self.assertTrue(success)
        
        user.refresh_from_db()
        self.assertFalse(user.is_active)
    
    def test_deactivate_nonexistent_user(self):
        """Test deactivating non-existent user returns False."""
        success = UserService.deactivate_user(99999)
        
        self.assertFalse(success)


# Run tests with: python manage.py test accounts.tests.test_services