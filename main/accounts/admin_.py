"""
Admin for the accounts application.

This module contains the admin for the accounts application.
"""
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import *
from django.conf import settings
from django.core.exceptions import ValidationError
from knox.models import AuthToken
from .models import *


# from django.contrib.auth import get_user_model
# PmrsUser = get_user_model(), 'img_preview'

class UserCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password.
    """
    def __init__(self, *args, **kwargs):        
        super().__init__(*args, **kwargs)        
        self.fields['first_name'].required = True  
        self.fields['last_name'].required = True  
        self.fields['email'].required = True  
        self.fields['user_img'].required = False  

    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = PmrsUser
        fields = ('__all__')
        # fields = ('username', 'first_name', 'last_name', 'email', 'is_active', 'priority', 'img_preview', 'user_img')

    def clean_password2(self):
        """
        Check that the two password entries match.
        """
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        """
        Save the user.
        """
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
        
class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the user change form.
        """
        super().__init__(*args, **kwargs)        
        self.fields['first_name'].required = True  
        self.fields['last_name'].required = True  
        self.fields['email'].required = True  
        self.fields['user_img'].required = False  

    password = ReadOnlyPasswordHashField()
    # label= ("Password"),
    #         help_text= ("Raw passwords are not stored, so there is no way to see "
    #                     "this user's password, but you can change the password "
    #                     "using this form."))
    class Meta:
        model = PmrsUser
        fields = ('__all__')
        # fields = ('username', 'first_name', 'last_name', 'email', 'is_active', 'priority', 'user_img')
    def clean_password(self):
        """
        Clean the password.
        """
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

class PmrsUserAdmin(UserAdmin):
    """
    Admin for the PmrsUser model.
    """
    # form = UserChangeForm
    # add_form = UserCreationForm  'personel', 

    list_display = ('username', 'personnel_code', 'email', 'full_name', 'is_active', 'priority')#, 'get_roles'
    readonly_fields = ['img_preview', 'last_login', 'date_joined']
    ordering = ('username',)
    list_filter = ['is_active'] 
    ordering = ['username']
    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)
    #     if request.user.is_superuser:
    #         return qs
    #     else:
    #         return qs.filter(user__is_superuser__exact=False)
    def get_actions(self, request):
        """
        Get the actions for the user admin.
        """
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    # def get_roles(self, obj):
    #     return ", ".join([r.role for r in obj.role_set.all()])
    
    # def save_model(self, request, obj, form, change):
    # # Override this to set the password to the value in the field if it's
    #     # changed.
    #     if obj.pk:
    #         orig_obj = models.User.objects.get(pk=obj.pk)
    #         if obj.password != orig_obj.password:
    #             obj.set_password(obj.password)
    #     else:
    #         obj.set_password(obj.password)
    #     obj.save()
        
    # get_roles.short_description = "Roles"

    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal info', {
            'fields': ('personnel_code', 'first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': (
                'is_active', 
                # 'is_staff', 'is_superuser', 'priority'
                # 'groups', 'user_permissions'
                )
        }),
        # ('Important dates', {
        #     'fields': ('last_login', 'date_joined')
        # }),
        ('User image', {
            'fields': ( 'img_preview', 'user_img')
        })
    )

    add_fieldsets = (
        (None, {
            'fields': ('username', 'password1', 'password2')
        }),
        ('Personal info', {
            'fields': ('personnel_code', 'first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': (
                'is_active', 
                # 'is_staff', 
                # 'is_superuser', 
                'priority'
                # 'groups', 'user_permissions'
                )
        }),
        # ('Important dates', {
        #     'fields': ('last_login', 'date_joined')
        # }),
        ('User image', {
            'fields': ( 'img_preview', 'user_img')
        })
    )
    
    search_fields = ('username',)
    

class UserAdmin(admin.ModelAdmin):
    """
    Admin for the User model.
    """
    list_display = ('userid', 'user', 'get_roles', 'active', 'priority')
    list_filter = ['active']
    search_fields = ['user']
    
    def get_actions(self, request):
        """
        Get the actions for the user admin.
        """
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    # def has_add_permission(self, request):
    #     return ("add" in request.path or "change" in request.path)
    
    def get_roles(self, obj):
        """
        Get the roles for the user.
        """
        return ", ".join([r.role for r in obj.role_set.all()])
    get_roles.short_description = "Roles"
    
    
class RoleAdmin(admin.ModelAdmin):
    """
    Admin for the Role model.
    """
    list_display = ('role', 'description')#, 'get_permissions'
    search_fields = ['role']
    ordering = ['role']

    def get_actions(self, request):
        """
        Get the actions for the role admin.
        """
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
    
    # def has_add_permission(self, request):
    #     return ("change" in request.path)
    
    def get_permissions(self, obj):
        """
        Get the permissions for the role.
        """
        return ", ".join([p.permission for p in obj.permission_set.all()])
    get_permissions.short_description = "Permissions"
    
    
class PermissionAdmin(admin.ModelAdmin):
    """
    Admin for the Permission model.
    """
    list_display = ('permission', 'description')
    search_fields = ['permission']
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions     
       
    # def has_add_permission(self, request):
    #     return ("add" in request.path or "change" in request.path)
   
    
class UserRoleAdmin(admin.ModelAdmin):
    """
    Admin for the UserRole model.
    """
    list_display = ('get_user', 'get_contract', 'get_role')
    search_fields = ['userid__username', 'projectid__contract', 'roleid__role']
    ordering = ['userid__username', 'projectid__contract', 'roleid__role']

    def get_actions(self, request):
        """
        Get the actions for the user role admin.
        """
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
    
    # def has_add_permission(self, request):
    #     return ("add" in request.path or "change" in request.path)

    
    @admin.display(ordering='UserRole__PmrsUser', description='user')
    def get_user(self, obj):
        """
        Get the user for the user role.
        """
        return obj.userid.username

    @admin.display(ordering='UserRole__Contract', description='project')
    def get_contract(self, obj):
        """
        Get the contract for the user role.
        """
        return obj.projectid.contract if obj.projectid is not None else None
        
    @admin.display(ordering='UserRole__Role', description='role')
    def get_role(self, obj):
        """
        Get the role for the user role.
        """
        return obj.roleid.role


class RolePermissionAdmin(admin.ModelAdmin):
    """
    Admin for the RolePermission model.
    """
    list_display = ('get_role', 'get_permission')
    # list_filter = ['permissionid']
    search_fields = ['roleid__role']
    ordering = ['roleid__role', 'permissionid__permission']
    
    @admin.display(ordering='RolePermission__Role', description='role')
    def get_role(self, obj):
        """
        Get the role for the role permission.
        """
        return obj.roleid.role
    
    @admin.display(ordering='RolePermission__Permission', description='permission')
    def get_permission(self, obj):
        """
        Get the permission for the role permission.
        """
        return obj.permissionid.permission
    
    def get_actions(self, request):
        """
        Get the actions for the role permission admin.
        """
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions   
    
    # def has_add_permission(self, request):
    #     return ("add" in request.path or "change" in request.path)
    
    
def get_app_list(self, request, app_label=None):
    """
    Get the app list for the admin.
    """
    app_dict = self._build_app_dict(request, app_label)
    
    if not app_dict:
        return
        
    NEW_ADMIN_ORDERING = []
    if app_label:
        for ao in settings.ADMIN_ORDERING:
            if ao[0] == app_label:
                NEW_ADMIN_ORDERING.append(ao)
                break
    
    if not app_label:
        for app_key in list(app_dict.keys()):
            if not any(app_key in ao_app for ao_app in settings.ADMIN_ORDERING):
                app_dict.pop(app_key)
    
    app_list = sorted(
        app_dict.values(), 
        key=lambda x: [ao[0] for ao in settings.ADMIN_ORDERING].index(x['app_label'])
    )
     
    for app, ao in zip(app_list, NEW_ADMIN_ORDERING or settings.ADMIN_ORDERING):
        if app['app_label'] == ao[0]:
            for model in list(app['models']):
                if not model['object_name'] in ao[1]:
                    app['models'].remove(model)
        app['models'].sort(key=lambda x: ao[1].index(x['object_name']))
    return app_list

admin.site.empty_value_display = "(None)"
admin.site.site_header = 'PMRS Admin Panel'
admin.site.site_title = 'PMRS'
admin.site.site_url = None
admin.AdminSite.get_app_list = get_app_list

# admin.site.register(User, UserAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Permission, PermissionAdmin)
admin.site.register(UserRole, UserRoleAdmin)
admin.site.register(RolePermission, RolePermissionAdmin)

# admin.py
# admin.site.unregister(User)
admin.site.register(PmrsUser, PmrsUserAdmin)
admin.site.unregister(Group)
admin.site.unregister(AuthToken)


