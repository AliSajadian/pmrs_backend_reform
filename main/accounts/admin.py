"""
Improved admin configuration for accounts application.

This module provides enhanced admin interfaces with:
- Better list displays and filtering
- Inline editing for related models
- Custom actions for bulk operations
- Improved search and ordering
- Read-only fields for sensitive data

To use this admin configuration:
1. In admin.py, import the classes from this file
2. Register the models with these admin classes instead of the old ones
"""
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.utils.html import format_html

from accounts.models import PmrsUser, Role, Permission, UserRole, RolePermission


class UserRoleInline(admin.TabularInline):
    """
    Inline admin for UserRole model.
    Allows editing user roles directly from the user admin page.
    """
    model = UserRole
    extra = 1
    fields = ('roleid', 'projectid', 'all_projects')
    autocomplete_fields = ['roleid', 'projectid']
    verbose_name = 'User Role Assignment'
    verbose_name_plural = 'User Role Assignments'


class RolePermissionInline(admin.TabularInline):
    """
    Inline admin for RolePermission model.
    Allows editing role permissions directly from the role admin page.
    """
    model = RolePermission
    extra = 1
    fields = ('permissionid',)
    autocomplete_fields = ['permissionid']
    verbose_name = 'Permission'
    verbose_name_plural = 'Permissions'


class PmrsUserCreationForm(forms.ModelForm):
    """Form for creating new users with password validation."""
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        help_text="Enter a strong password"
    )
    password2 = forms.CharField(
        label='Password confirmation',
        widget=forms.PasswordInput,
        help_text="Enter the same password as before, for verification"
    )
    
    class Meta:
        model = PmrsUser
        fields = ('username', 'email', 'first_name', 'last_name', 'personnel_code', 'user_img')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
    
    def clean_password2(self):
        """Check that the two password entries match."""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2
    
    def save(self, commit=True):
        """Save user with hashed password."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class PmrsUserChangeForm(forms.ModelForm):
    """Form for updating users with read-only password hash."""
    password = ReadOnlyPasswordHashField(
        label="Password",
        help_text=(
            "Raw passwords are not stored, so there is no way to see this user's password, "
            "but you can change the password using <a href=\"../password/\">this form</a>."
        )
    )
    
    class Meta:
        model = PmrsUser
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
    
    def clean_password(self):
        """Return the initial password value."""
        return self.initial.get("password")


@admin.register(PmrsUser)
class PmrsUserAdmin1(BaseUserAdmin):
    """
    Enhanced admin for PmrsUser model with inline role editing and better UI.
    """
    form = PmrsUserChangeForm
    add_form = PmrsUserCreationForm
    
    list_display = (
        'username',
        'personnel_code',
        'full_name',
        'email',
        'is_active',
        'priority',
        'role_count',
        'last_login_display',
        'user_image_thumbnail'
    )
    
    list_filter = (
        'is_active',
        'is_staff',
        'is_superuser',
        'priority',
        'date_joined',
        'last_login',
    )
    
    search_fields = (
        'username',
        'first_name',
        'last_name',
        'email',
        'personnel_code'
    )
    
    ordering = ('username',)
    
    readonly_fields = (
        'img_preview',
        'last_login',
        'date_joined',
        'role_count'
    )
    
    inlines = [UserRoleInline]
    
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal Information', {
            'fields': ('personnel_code', 'first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'priority'),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
        ('User Image', {
            'fields': ('img_preview', 'user_img')
        }),
        ('Statistics', {
            'fields': ('role_count',),
            'classes': ('collapse',)
        })
    )
    
    add_fieldsets = (
        (None, {
            'fields': ('username', 'password1', 'password2')
        }),
        ('Personal Information', {
            'fields': ('personnel_code', 'first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'priority')
        }),
        ('User Image', {
            'fields': ('user_img',)
        })
    )
    
    actions = ['activate_users', 'deactivate_users', 'reset_priority']
    
    def role_count(self, obj):
        """Display count of roles assigned to user."""
        count = UserRole.objects.filter(userid=obj).count()
        return count
    role_count.short_description = 'Roles'
    
    def last_login_display(self, obj):
        """Display last login with better formatting."""
        if obj.last_login:
            return obj.last_login.strftime('%Y-%m-%d %H:%M')
        return 'Never'
    last_login_display.short_description = 'Last Login'
    
    def user_image_thumbnail(self, obj):
        """Display small thumbnail of user image."""
        if obj.user_img and hasattr(obj.user_img, 'url'):
            return format_html(
                '<img src="{}" width="30" height="30" style="border-radius: 50%;" />',
                obj.user_img.url
            )
        return '—'
    user_image_thumbnail.short_description = 'Image'
    
    def activate_users(self, request, queryset):
        """Bulk action to activate users."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} user(s) activated successfully.')
    activate_users.short_description = 'Activate selected users'
    
    def deactivate_users(self, request, queryset):
        """Bulk action to deactivate users."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} user(s) deactivated successfully.')
    deactivate_users.short_description = 'Deactivate selected users'
    
    def reset_priority(self, request, queryset):
        """Bulk action to reset priority to 0."""
        updated = queryset.update(priority=0)
        self.message_user(request, f'Priority reset for {updated} user(s).')
    reset_priority.short_description = 'Reset priority to 0'
    
    def get_queryset(self, request):
        """Optimize queryset with annotations."""
        qs = super().get_queryset(request)
        return qs.prefetch_related('user_userrole__roleid')


@admin.register(Role)
class RoleAdmin1(admin.ModelAdmin):
    """
    Enhanced admin for Role model with permission inline editing.
    """
    list_display = (
        'role',
        'description',
        'permission_count',
        'user_count'
    )
    
    search_fields = ('role', 'description')
    ordering = ('role',)
    
    inlines = [RolePermissionInline]
    
    actions = ['duplicate_role']
    
    def permission_count(self, obj):
        """Display count of permissions for this role."""
        count = RolePermission.objects.filter(roleid=obj).count()
        return count
    permission_count.short_description = 'Permissions'
    
    def user_count(self, obj):
        """Display count of users with this role."""
        count = UserRole.objects.filter(roleid=obj).values('userid').distinct().count()
        return count
    user_count.short_description = 'Users'
    
    def duplicate_role(self, request, queryset):
        """Duplicate selected role with all permissions."""
        for role in queryset:
            # Get all permissions for this role
            permissions = RolePermission.objects.filter(roleid=role)
            
            # Create new role
            new_role = Role.objects.create(
                role=f"{role.role} (Copy)",
                description=role.description
            )
            
            # Copy permissions
            for perm in permissions:
                RolePermission.objects.create(
                    roleid=new_role,
                    permissionid=perm.permissionid
                )
            
            self.message_user(request, f'Role "{role.role}" duplicated as "{new_role.role}".')
    duplicate_role.short_description = 'Duplicate selected role(s)'


@admin.register(Permission)
class PermissionAdmin1(admin.ModelAdmin):
    """
    Enhanced admin for Permission model with better display and filtering.
    """
    list_display = (
        'permission',
        'description',
        'role_count',
        'category'
    )
    
    list_filter = ('permission',)
    search_fields = ('permission', 'description')
    ordering = ('permission',)
    
    def role_count(self, obj):
        """Display count of roles with this permission."""
        count = RolePermission.objects.filter(permissionid=obj).count()
        return count
    role_count.short_description = 'Roles'
    
    def category(self, obj):
        """Extract category from permission name (e.g., 'Budget R/W' -> 'Budget')."""
        perm_name = str(obj.permission)
        if ' ' in perm_name:
            return perm_name.split(' ')[0]
        return 'General'
    category.short_description = 'Category'


@admin.register(UserRole)
class UserRoleAdmin1(admin.ModelAdmin):
    """
    Enhanced admin for UserRole model with better filtering and display.
    """
    list_display = (
        'get_user',
        'get_user_personnel_code',
        'get_role',
        'get_project',
        'all_projects',
        'permission_summary'
    )
    
    list_filter = (
        'roleid__role',
        'all_projects',
        'projectid__contract'
    )
    
    search_fields = (
        'userid__username',
        'userid__first_name',
        'userid__last_name',
        'userid__personnel_code',
        'projectid__contract',
        'roleid__role'
    )
    
    autocomplete_fields = ['userid', 'roleid', 'projectid']
    
    ordering = ('userid__username', 'projectid__contract', 'roleid__role')
    
    actions = ['assign_all_projects']
    
    def get_user(self, obj):
        """Display user's full name and username."""
        return f"{obj.userid.first_name} {obj.userid.last_name} ({obj.userid.username})"
    get_user.short_description = 'User'
    get_user.admin_order_field = 'userid__username'
    
    def get_user_personnel_code(self, obj):
        """Display user's personnel code."""
        return obj.userid.personnel_code or '—'
    get_user_personnel_code.short_description = 'Personnel Code'
    get_user_personnel_code.admin_order_field = 'userid__personnel_code'
    
    def get_role(self, obj):
        """Display role name."""
        return str(obj.roleid.role)
    get_role.short_description = 'Role'
    get_role.admin_order_field = 'roleid__role'
    
    def get_project(self, obj):
        """Display project/contract name."""
        if obj.all_projects:
            return format_html('<strong>ALL PROJECTS</strong>')
        return str(obj.projectid.contract) if obj.projectid else '—'
    get_project.short_description = 'Project/Contract'
    get_project.admin_order_field = 'projectid__contract'
    
    def permission_summary(self, obj):
        """Display count of permissions for this role."""
        count = RolePermission.objects.filter(roleid=obj.roleid).count()
        return f"{count} permission(s)"
    permission_summary.short_description = 'Permissions'
    
    def assign_all_projects(self, request, queryset):
        """Assign selected user roles to all projects."""
        updated = queryset.update(all_projects=True, projectid=None)
        self.message_user(request, f'{updated} user role(s) assigned to all projects.')
    assign_all_projects.short_description = 'Assign to all projects'


@admin.register(RolePermission)
class RolePermissionAdmin1(admin.ModelAdmin):
    """
    Enhanced admin for RolePermission model.
    """
    list_display = (
        'get_role',
        'get_permission',
        'permission_category',
        'users_with_role'
    )
    
    list_filter = (
        'roleid__role',
        'permissionid__permission'
    )
    
    search_fields = (
        'roleid__role',
        'permissionid__permission'
    )
    
    autocomplete_fields = ['roleid', 'permissionid']
    
    ordering = ('roleid__role', 'permissionid__permission')
    
    def get_role(self, obj):
        """Display role name."""
        return str(obj.roleid.role)
    get_role.short_description = 'Role'
    get_role.admin_order_field = 'roleid__role'
    
    def get_permission(self, obj):
        """Display permission name."""
        return str(obj.permissionid.permission)
    get_permission.short_description = 'Permission'
    get_permission.admin_order_field = 'permissionid__permission'
    
    def permission_category(self, obj):
        """Extract category from permission name."""
        perm_name = str(obj.permissionid.permission)
        if ' ' in perm_name:
            return perm_name.split(' ', maxsplit=1)[0]
        return 'General'
    permission_category.short_description = 'Category'
    
    def users_with_role(self, obj):
        """Display count of users with this role."""
        count = UserRole.objects.filter(roleid=obj.roleid).values('userid').distinct().count()
        return f"{count} user(s)"
    users_with_role.short_description = 'Users'

