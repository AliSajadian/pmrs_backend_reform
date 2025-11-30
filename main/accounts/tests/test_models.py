"""
Unit tests for accounts models.
Tests model methods, properties, and custom manager methods.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from accounts.models import (
    PmrsUser, User, Role, Permission, UserRole, RolePermission
)
from contracts.models import Contract

User = get_user_model()


class PmrsUserModelTest(TestCase):
    """Test PmrsUser custom user model."""
    
    def test_create_user_with_manager(self):
        """Test creating user with custom manager."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
    
    def test_create_superuser_with_manager(self):
        """Test creating superuser with custom manager."""
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        self.assertEqual(user.username, 'admin')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
    
    def test_create_user_without_username_raises_error(self):
        """Test that creating user without username raises error."""
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(
                username='',
                email='test@example.com',
                password='testpass123'
            )
        self.assertIn('Users must have an username', str(context.exception))
    
    def test_full_name_method(self):
        """Test full_name method returns formatted name."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        self.assertEqual(user.full_name(), 'John, Doe')
    
    def test_str_method(self):
        """Test __str__ method returns username."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.assertEqual(str(user), 'testuser')
    
    def test_user_with_personnel_code(self):
        """Test user with personnel code."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            personnel_code=12345
        )
        
        self.assertEqual(user.personnel_code, 12345)
    
    def test_user_img_default(self):
        """Test default user image."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.assertIsNotNone(user.user_img)
    
    def test_img_preview_with_image(self):
        """Test img_preview method with uploaded image."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create a simple test image
        image_file = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'',
            content_type='image/jpeg'
        )
        user.user_img = image_file
        user.save()
        
        preview = user.img_preview()
        self.assertIn('<img', preview)
        self.assertIn('width = "120"', preview)
    
    def test_priority_default_value(self):
        """Test priority field has default value."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.assertEqual(user.priority, 0)


class RoleModelTest(TestCase):
    """Test Role model."""
    
    def test_create_role(self):
        """Test creating a role."""
        role = Role.objects.create(
            role='Manager',
            description='Project Manager Role'
        )
        
        self.assertEqual(role.role, 'Manager')
        self.assertEqual(role.description, 'Project Manager Role')
    
    def test_str_method(self):
        """Test __str__ method returns role name."""
        role = Role.objects.create(role='Admin')
        
        self.assertEqual(str(role), 'Admin')
    
    def test_role_unique_constraint(self):
        """Test that role name is unique."""
        Role.objects.create(role='Manager')
        
        with self.assertRaises(Exception):
            Role.objects.create(role='Manager')


class PermissionModelTest(TestCase):
    """Test Permission model."""
    
    def test_create_permission(self):
        """Test creating a permission."""
        permission = Permission.objects.create(
            permission='View Reports',
            description='Can view all reports'
        )
        
        self.assertEqual(permission.permission, 'View Reports')
        self.assertEqual(permission.description, 'Can view all reports')
    
    def test_str_method(self):
        """Test __str__ method returns permission name."""
        permission = Permission.objects.create(permission='Edit Users')
        
        self.assertEqual(str(permission), 'Edit Users')
    
    def test_permission_unique_constraint(self):
        """Test that permission name is unique."""
        Permission.objects.create(permission='View Reports')
        
        with self.assertRaises(Exception):
            Permission.objects.create(permission='View Reports')


class UserRoleModelTest(TestCase):
    """Test UserRole model and its methods."""
    
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
        
        self.role = Role.objects.create(
            role='Project Manager',
            description='Manager role'
        )
        
        self.permission1 = Permission.objects.create(
            permission='Financial Info R/W',
            description='Read/Write Financial Info'
        )
        
        self.permission2 = Permission.objects.create(
            permission='HSE R/W',
            description='Read/Write HSE'
        )
    
    def test_create_user_role(self):
        """Test creating a user role."""
        user_role = UserRole.objects.create(
            userid=self.user,
            projectid=self.contract,
            roleid=self.role,
            all_projects=False
        )
        
        self.assertEqual(user_role.userid, self.user)
        self.assertEqual(user_role.projectid, self.contract)
        self.assertEqual(user_role.roleid, self.role)
    
    def test_user_role_with_all_projects(self):
        """Test user role with all_projects flag."""
        user_role = UserRole.objects.create(
            userid=self.user,
            roleid=self.role,
            all_projects=True
        )
        
        self.assertTrue(user_role.all_projects)
        self.assertIsNone(user_role.projectid)
    
    def test_permissions_method(self):
        """Test permissions method returns role permissions."""
        # Create role permissions
        RolePermission.objects.create(
            roleid=self.role,
            permissionid=self.permission1
        )
        RolePermission.objects.create(
            roleid=self.role,
            permissionid=self.permission2
        )
        
        user_role = UserRole.objects.create(
            userid=self.user,
            projectid=self.contract,
            roleid=self.role
        )
        
        permissions = user_role.permissions()
        permission_names = [p['permission'] for p in permissions]
        
        self.assertIn('Financial Info R/W', permission_names)
        self.assertIn('HSE R/W', permission_names)
    
    def test_board_method_returns_true_for_board_role(self):
        """Test board method returns True for board role."""
        board_role = Role.objects.create(role='Board Member')
        user_role = UserRole.objects.create(
            userid=self.user,
            roleid=board_role
        )
        
        self.assertTrue(user_role.board())
    
    def test_board_method_returns_false_for_non_board_role(self):
        """Test board method returns False for non-board role."""
        user_role = UserRole.objects.create(
            userid=self.user,
            roleid=self.role
        )
        
        self.assertFalse(user_role.board())
    
    def test_admin_method_returns_true_for_admin_role(self):
        """Test admin method returns True for admin role."""
        admin_role = Role.objects.create(role='System Admin')
        user_role = UserRole.objects.create(
            userid=self.user,
            roleid=admin_role
        )
        
        self.assertTrue(user_role.admin())
    
    def test_admin_method_returns_false_for_non_admin_role(self):
        """Test admin method returns False for non-admin role."""
        user_role = UserRole.objects.create(
            userid=self.user,
            roleid=self.role
        )
        
        self.assertFalse(user_role.admin())
    
    def test_financial_info_confirmor(self):
        """Test financial_info_confirmor method."""
        # Create role with financial info permission
        RolePermission.objects.create(
            roleid=self.role,
            permissionid=self.permission1
        )
        
        user_role = UserRole.objects.create(
            userid=self.user,
            projectid=self.contract,
            roleid=self.role
        )
        
        confirmor = user_role.financial_info_confirmor()
        self.assertEqual(confirmor, 'Test, User')
    
    def test_hse_confirmor(self):
        """Test hse_confirmor method."""
        # Create role with HSE permission
        RolePermission.objects.create(
            roleid=self.role,
            permissionid=self.permission2
        )
        
        user_role = UserRole.objects.create(
            userid=self.user,
            projectid=self.contract,
            roleid=self.role
        )
        
        confirmor = user_role.hse_confirmor()
        self.assertEqual(confirmor, 'Test, User')
    
    def test_confirmor_returns_empty_when_multiple_users(self):
        """Test confirmor returns empty string when multiple users have permission."""
        # Create second user with same role
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123',
            first_name='Test2',
            last_name='User2'
        )
        
        RolePermission.objects.create(
            roleid=self.role,
            permissionid=self.permission1
        )
        
        UserRole.objects.create(
            userid=self.user,
            projectid=self.contract,
            roleid=self.role
        )
        
        UserRole.objects.create(
            userid=user2,
            projectid=self.contract,
            roleid=self.role
        )
        
        user_role = UserRole.objects.first()
        confirmor = user_role.financial_info_confirmor()
        
        # Should return empty string when multiple users
        self.assertEqual(confirmor, '')


class RolePermissionModelTest(TestCase):
    """Test RolePermission model."""
    
    def setUp(self):
        """Set up test data."""
        self.role = Role.objects.create(role='Manager')
        self.permission = Permission.objects.create(permission='View Reports')
    
    def test_create_role_permission(self):
        """Test creating a role permission."""
        role_permission = RolePermission.objects.create(
            roleid=self.role,
            permissionid=self.permission
        )
        
        self.assertEqual(role_permission.roleid, self.role)
        self.assertEqual(role_permission.permissionid, self.permission)
    
    def test_role_can_have_multiple_permissions(self):
        """Test that a role can have multiple permissions."""
        perm1 = Permission.objects.create(permission='Edit Reports')
        perm2 = Permission.objects.create(permission='Delete Reports')
        
        RolePermission.objects.create(roleid=self.role, permissionid=self.permission)
        RolePermission.objects.create(roleid=self.role, permissionid=perm1)
        RolePermission.objects.create(roleid=self.role, permissionid=perm2)
        
        role_perms = RolePermission.objects.filter(roleid=self.role)
        self.assertEqual(role_perms.count(), 3)


# Run tests with: python manage.py test accounts.tests.test_models