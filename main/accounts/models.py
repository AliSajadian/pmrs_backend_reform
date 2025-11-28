"""
Models for the accounts application.

This module contains the models for the accounts application.
"""
from django.db import models
from django.db.models import F
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
from django.utils.html import mark_safe
from django.contrib.auth import get_user_model

from contracts.models import Contract
# Create your models here.

def upload_to(filename):
    """
    Get the upload path for the user image.
    """
    return f"assets/{filename}".format(filename=filename)

def upload_path(instance, filename):
    """
    Get the upload path for the user image.
    """
    return '/'.join(['user', instance.user_img, filename])


class PmrsUserManager(BaseUserManager):
    """
    Manager for the PmrsUser model.
    """
    def create_user(self, username, email, password=None, **kwargs):
        """
        Creates and saves a User with the given username and password.
        """
        if not username:
            raise ValueError("Users must have an username")

        user = self.model(
            username=username,
            email=self.normalize_email(email),
            is_staff=True,
            is_superuser=True,
            **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            username,
            email=email,
            password=password,
        )
        user.is_superuser = True
        user.save(using=self._db)
        return user


class PmrsUser(AbstractUser):
    """
    User model for the accounts application.
    """
    first_name = models.CharField(max_length=30, blank=False, null=False)
    last_name = models.CharField(max_length=50, blank=False, null=False)
    personnel_code = models.PositiveIntegerField(null=True)
    email = models.EmailField(max_length=150, blank=False, null=True)
    user_img = models.ImageField(
        upload_to='user_images',
        default='user_images/asft.png',
        null=True,
        blank=True)

    priority = models.SmallIntegerField(db_column='Priority', default=0)

    objects = PmrsUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def img_preview(self): #new
        """
        Get the image preview for the user.
        """
        if self.user_img and hasattr(self.user_img, 'url'):
            image_url = self.user_img.url
            return mark_safe(f'<img src = "{image_url}" width = "120", alt="img"/>')

        return mark_safe('<img src = "/assets/user_images/asft.png" width = "120", alt="img"/>')

    def __str__(self) -> str:
        return str(self.username) if self.username else ""

    def full_name(self):
        """
        Get the full name of the user.
        """
        return f"{self.first_name}, {self.last_name}"


class User(models.Model):
    """
    User model for the accounts application.
    """
    userid = models.IntegerField(db_column='UserID', primary_key=True)
    user = models.CharField(db_column='User', unique=True, max_length=50,
            db_collation='SQL_Latin1_General_CP1_CI_AS')
    passphrase = models.CharField(db_column='PassPhrase', max_length=100,
            db_collation='SQL_Latin1_General_CP1_CI_AS')
    active = models.BooleanField(db_column='Active')
    priority = models.SmallIntegerField(db_column='Priority')

    def __str__(self) -> str:
        return str(self.user) if self.user else ""

    class Meta:
        db_table = 'tbl_User'
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Userlogin(models.Model):
    """
    User login model for the accounts application.
    """
    loginid = models.AutoField(db_column='LoginID', primary_key=True)
    userid = models.IntegerField(db_column='UserID')
    enterdate = models.DateTimeField(db_column='EnterDate')
    exitdate = models.DateTimeField(db_column='ExitDate', blank=True, null=True)

    class Meta:
        db_table = 'tbl_UserLogin'


class Role(models.Model):
    """
    Role model for the accounts application.
    """
    roleid = models.AutoField(db_column='RoleID', primary_key=True)
    user = models.ManyToManyField(settings.AUTH_USER_MODEL, through='UserRole')
    role = models.CharField(db_column='Role', unique=True, max_length=50,
            db_collation='SQL_Latin1_General_CP1_CI_AS')
    description = models.CharField(db_column='Description', max_length=50,
            db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)

    def __str__(self) -> str:
        return str(self.role) if self.role else ""

    class Meta:
        db_table = 'tbl_Role'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'


class Permission(models.Model):
    """
    Permission model for the accounts application.
    """
    permissionid = models.AutoField(db_column='PermissionID', primary_key=True)
    role = models.ManyToManyField(Role, through='RolePermission')
    permission = models.CharField(db_column='Permission', unique=True,
            max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS')
    description = models.CharField(db_column='Description', max_length=50,
            db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)

    def __str__(self) -> str:
        return str(self.permission) if self.permission else ""

    class Meta:
        db_table = 'tbl_Permission'
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'


class UserRole(models.Model):
    """
    User role model for the accounts application.
    """
    userroleid = models.AutoField(db_column='UserRoleID', primary_key=True)
    userid = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="User_UserRole",
            on_delete=models.PROTECT, db_column='UserID')
    projectid = models.ForeignKey(Contract, related_name="Contract_UserRole",
            on_delete=models.PROTECT, blank=True, null=True, db_column='ContractID')
    roleid = models.ForeignKey(Role, related_name="Role_UserRole",
            on_delete=models.PROTECT, db_column='RoleID')
    all_projects = models.BooleanField(db_column='AllProjects', default=False, null=True)

    def permissions(self):
        """
        Get the permissions for the user role.
        """
        # permissions = RolePermission.objects.filter(
        # roleid__exact=self.roleid.roleid).values('permissionid')
        permissions = RolePermission.objects.filter(
            roleid__exact=self.roleid.roleid).values(
            'permissionid__permission').annotate(permission = 
            F('permissionid__permission')).values('permission')
        return permissions

    def board(self):
        """
        Get the board for the user role.
        """
        # if self.roleid and hasattr(self.roleid, 'role'):
        #     pass
        return str(self.roleid.role).lower().find('board') > -1

    def admin(self):
        """
        Get the admin for the user role.
        """
        return str(self.roleid.role).lower().find('admin') > -1

    def project_manager(self):
        """
        Get the project manager for the user role.
        """
        user = get_user_model().objects.get(pk=self.projectid.projectmanagerid.id)
        return f"{user.first_name}, {user.last_name}"

    def financial_info_confirmor(self):
        """
        Get the financial info confirmor for the user role.
        """
        roles = RolePermission.objects.filter(
            permissionid__permission__exact='Financial Info R/W').values('roleid')
        users = UserRole.objects.filter(projectid__exact=self.projectid, roleid__in=roles)

        if len(users) == 1:
            return f"{users[0].userid.first_name}, {users[0].userid.last_name}"
        return ""

    def hse_confirmor(self):
        """
        Get the hse confirmor for the user role.
        """
        roles = RolePermission.objects.filter(
            permissionid__permission__exact='HSE R/W').values('roleid')
        users = UserRole.objects.filter(projectid__exact=self.projectid, roleid__in=roles)

        if len(users) == 1:
            return f"{users[0].userid.first_name}, {users[0].userid.last_name}"
        return ""

    def progress_state_confirmor(self):
        """
        Get the progress state confirmor for the user role.
        """
        roles = RolePermission.objects.filter(
            permissionid__permission__exact='Progress State R/W').values('roleid')
        users = UserRole.objects.filter(projectid__exact=self.projectid, roleid__in=roles)

        if len(users) == 1:
            return f"{users[0].userid.first_name}, {users[0].userid.last_name}"
        return ""

    def time_progress_state_confirmor(self):
        """
        Get the time progress state confirmor for the user role.
        """
        roles = RolePermission.objects.filter(
            permissionid__permission__exact='Time Progress State R/W').values('roleid')
        users = UserRole.objects.filter(projectid__exact=self.projectid, roleid__in=roles)

        if len(users) == 1:
            return f"{users[0].userid.first_name}, {users[0].userid.last_name}"
        return ""

    def invoice_confirmor(self):
        """
        Get the invoice confirmor for the user role.
        """
        roles = RolePermission.objects.filter(
            permissionid__permission__exact='Invoices R/W').values('roleid')
        users = UserRole.objects.filter(projectid__exact=self.projectid, roleid__in=roles)

        if len(users) == 1:
            return f"{users[0].userid.first_name}, {users[0].userid.last_name}"
        else:
            return ""

    def financial_invoice_confirmor(self):
        """
        Get the financial invoice confirmor for the user role.
        """
        roles = RolePermission.objects.filter(
            permissionid__permission__exact='Invoice Financial R/W').values('roleid')
        users = UserRole.objects.filter(projectid__exact=self.projectid, roleid__in=roles)

        if len(users) == 1:
            return f"{users[0].userid.first_name}, {users[0].userid.last_name}"
        return ""

    def work_volume_confirmor(self):
        """
        Get the work volume confirmor for the user role.
        """
        roles = RolePermission.objects.filter(
            permissionid__permission__exact='Work Volume Done R/W').values('roleid')
        users = UserRole.objects.filter(projectid__exact=self.projectid, roleid__in=roles)

        if len(users) == 1:
            return f"{users[0].userid.first_name}, {users[0].userid.last_name}"
        else:
            return ""

    def pms_progress_confirmor(self):
        """
        Get the pms progress confirmor for the user role.
        """
        roles = RolePermission.objects.filter(
            permissionid__permission__exact='PMS Progress R/W').values('roleid')
        users = UserRole.objects.filter(projectid__exact=self.projectid, roleid__in=roles)

        if len(users) == 1:
            return f"{users[0].userid.first_name}, {users[0].userid.last_name}"
        return ""

    def budget_confirmor(self):
        """
        Get the budget confirmor for the user role.
        """
        roles = RolePermission.objects.filter(
            permissionid__permission__exact='Budget R/W').values('roleid')
        users = UserRole.objects.filter(projectid__exact=self.projectid, roleid__in=roles)

        if len(users) == 1:
            return f"{users[0].userid.first_name}, {users[0].userid.last_name}"
        return ""

    def machinary_confirmor(self):
        """
        Get the machinary confirmor for the user role.
        """
        roles = RolePermission.objects.filter(
            permissionid__permission__exact='Machinary R/W').values('roleid')
        users = UserRole.objects.filter(projectid__exact=self.projectid, roleid__in=roles)

        if len(users) == 1:
            return f"{users[0].userid.first_name}, {users[0].userid.last_name}"
        return ""

    def project_personel_confirmor(self):
        """
        Get the project personel confirmor for the user role.
        """
        roles = RolePermission.objects.filter(
            permissionid__permission__exact='Project Personel R/W').values('roleid')
        users = UserRole.objects.filter(projectid__exact=self.projectid, roleid__in=roles)

        if len(users) == 1:
            return f"{users[0].userid.first_name}, {users[0].userid.last_name}"
        return ""

    def problem_confirmor(self):
        """
        Get the problem confirmor for the user role.
        """
        roles = RolePermission.objects.filter(
            permissionid__permission__exact='Problems R/W').values('roleid')
        users = UserRole.objects.filter(projectid__exact=self.projectid, roleid__in=roles)

        if len(users) == 1:
            return f"{users[0].userid.first_name}, {users[0].userid.last_name}"
        return ""

    def critical_action_confirmor(self):
        """
        Get the critical action confirmor for the user role.
        """
        roles = RolePermission.objects.filter(
            permissionid__permission__exact='Critical Action R/W').values('roleid')
        users = UserRole.objects.filter(projectid__exact=self.projectid, roleid__in=roles)

        if len(users) == 1:
            return f"{users[0].userid.first_name}, {users[0].userid.last_name}"
        return ""

    def project_dox_confirmor(self):
        """
        Get the project dox confirmor for the user role.
        """
        roles = RolePermission.objects.filter(
            permissionid__permission__exact='Project Documents R/W').values('roleid')
        users = UserRole.objects.filter(projectid__exact=self.projectid, roleid__in=roles)

        if len(users) == 1:
            return f"{users[0].userid.first_name}, {users[0].userid.last_name}"
        return ""

    def periodic_dox_confirmor(self):
        """
        Get the periodic dox confirmor for the user role.
        """
        roles = RolePermission.objects.filter(
            permissionid__permission__exact='Periodic Documents R/W').values('roleid')
        users = UserRole.objects.filter(projectid__exact=self.projectid, roleid__in=roles)

        if len(users) == 1:
            return f"{users[0].userid.first_name}, {users[0].userid.last_name}"
        return ""

    def zone_image_confirmor(self):
        """
        Get the zone image confirmor for the user role.
        """
        roles = RolePermission.objects.filter(
            permissionid__permission__exact='Zone R/W').values('roleid')
        users = UserRole.objects.filter(projectid__exact=self.projectid, roleid__in=roles)

        if len(users) == 1:
            return f"{users[0].userid.first_name}, {users[0].userid.last_name}"
        return ""

    class Meta:
        db_table = 'tbl_JUserRole'
        verbose_name = 'User_Project_Role'
        verbose_name_plural = 'User_Projects_Roles'


class RolePermission(models.Model):
    """
    Role permission model for the accounts application.
    """
    rolepermissionid = models.AutoField(db_column='RolePermissionID', primary_key=True)
    roleid = models.ForeignKey(Role, related_name="Role_RolePermission",
            on_delete=models.PROTECT, db_column='RoleID')
    permissionid = models.ForeignKey(Permission, related_name="Permission_RolePermission",
            on_delete=models.PROTECT, db_column='PermissionID')

    class Meta:
        db_table = 'tbl_JRolePermission'
        verbose_name = 'Role_Permission'
        verbose_name_plural = 'Role_Permissions'
