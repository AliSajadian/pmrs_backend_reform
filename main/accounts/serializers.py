"""data
data
data
data
Serializers for the accounts application.

This module contains the serializers for the accounts application.
"""
import logging
from rest_framework import serializers
from django.contrib.auth import get_user_model

from django.contrib.auth.models import Group, Permission

from accounts.models import User, UserRole


#=========== Authorization Serializers ============
class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    """
    full_name = serializers.ReadOnlyField()
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'email', 'full_name', 'user_img')

class UserExSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    """
    class Meta:
        model = get_user_model()
        fields = ('id', 'first_name', 'last_name', 'username', 'email', 'is_active')

class GroupSerializer(serializers.ModelSerializer):
    """
    Serializer for the Group model.
    """
    class Meta:
        model = Group
        fields = ('id', 'name')

class PermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Permission model.
    """
    class Meta:
        model = Permission
        fields = ('id', 'name')

class UserGroupSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserGroup model.
    """
    groups = serializers.PrimaryKeyRelatedField(many=True, queryset=Group.objects.all())

    class Meta:
        model = get_user_model()
        fields = ['id', 'groups']

class UserGroupsExSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserGroupsEx model.
    """
    groups = GroupSerializer(many=True)
    # serializers.PrimaryKeyRelatedField(many=True, queryset=Group.objects.all())

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'first_name', 'last_name', 'groups')

class GroupPermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for the GroupPermission model.
    """
    permissions = serializers.PrimaryKeyRelatedField(many=True, queryset=Permission.objects.all())

    class Meta:
        model = Group
        fields = ['id', 'permissions']

class GroupPermissionsExSerializer(serializers.ModelSerializer):
    """
    Serializer for the GroupPermissionsEx model.
    """
    permissions = PermissionSerializer(many=True)

    class Meta:
        model = Group
        fields = ('id', 'name', 'permissions')

class UserPermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserPermission model.
    """
    user_permissions = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Permission.objects.all())

    class Meta:
        model = get_user_model()
        fields = ['id', 'user_permissions']

class UserPermissionsExSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserPermissionsEx model.
    """
    user_permissions = PermissionSerializer(many=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'first_name', 'last_name', 'user_permissions')

class UserContractPermissionsSerializers(serializers.ModelSerializer):
    """
    Serializer for the UserContractPermissions model.
    """
    permissions = serializers.ReadOnlyField()
    board = serializers.ReadOnlyField()
    admin = serializers.ReadOnlyField()

    class Meta:
        model = UserRole
        fields = ['userid', 'projectid', 'board', 'admin', 'permissions']

class ProjectConfirmersSerializers(serializers.ModelSerializer):
    """
    Serializer for the ProjectConfirmers model.
    """
    project_manager = serializers.ReadOnlyField()
    financialInfo_confirmor = serializers.ReadOnlyField()
    hse_confirmor = serializers.ReadOnlyField()
    progressState_confirmor = serializers.ReadOnlyField()
    timeProgressState_confirmor = serializers.ReadOnlyField()
    invoice_confirmor = serializers.ReadOnlyField()
    financialInvoice_confirmor = serializers.ReadOnlyField()
    workVolume_confirmor = serializers.ReadOnlyField()
    pmsProgress_confirmor = serializers.ReadOnlyField()
    budget_confirmor = serializers.ReadOnlyField()
    machinary_confirmor = serializers.ReadOnlyField()
    projectPersonel_confirmor = serializers.ReadOnlyField()
    problem_confirmor = serializers.ReadOnlyField()
    criticalAction_confirmor = serializers.ReadOnlyField()
    projectDox_confirmor = serializers.ReadOnlyField()
    periodicDox_confirmor = serializers.ReadOnlyField()
    zoneImage_confirmor = serializers.ReadOnlyField()

    class Meta:
        model = UserRole
        fields = ['project_manager', 'financialInfo_confirmor', 'hse_confirmor',
                  'progressState_confirmor','timeProgressState_confirmor', 'invoice_confirmor',  
                  'financialInvoice_confirmor','workVolume_confirmor', 'pmsProgress_confirmor',     
                  'projectPersonel_confirmor', 'problem_confirmor', 'criticalAction_confirmor', 
                  'budget_confirmor', 'machinary_confirmor', 'projectDox_confirmor',
                  'periodicDox_confirmor', 'zoneImage_confirmor']  


#=========== Authentication Serializers ============
class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for the Register model.
    """
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = get_user_model().objects.create_user(validated_data['username'],
        validated_data['email'], validated_data['password'])

        return user

class LoginSerializer(serializers.Serializer):
    """
    Serializer for the Login model.
    """
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        """
        Validate the login attrs.
        """
        logger = logging.getLogger(__name__)

        # Get the request from the context
        # request = self.context.get('request')
        username = attrs.get('username')
        password = attrs.get('password')

        # First, check if user exists
        user_1 = get_user_model()
        try:
            user = user_1.objects.get(username=username)
            print(f"User found: {user.username}, is_active: {user.is_active}")
            logger.info(lambda: f"User found: %{username}, is_active: {user.is_active}")

            # Debug: Check password
            password_valid = user.check_password(password)
            logger.info(lambda: f"Password check result: {password_valid}")

            if password_valid and user.is_active:
                print("Password matches!")
                return user

            if not password_valid:
                raise serializers.ValidationError("Incorrect password")

            print("Password does not match!")
            raise serializers.ValidationError("User account is disabled")

        except User.DoesNotExist as e:
            print("User does not exist!")
            logger.error(lambda: f"User not found: {username}")
            raise serializers.ValidationError("User not found") from e

    def create(self, validated_data):
        # Since this is only for validation, return None or the user
        return validated_data.get('user')

    def update(self, instance, validated_data):
        # Not used for login
        return instance


class PasswordSerializer(serializers.Serializer):
    """
    Serializer for the Password model.
    """
    userid = serializers.IntegerField()
    username = serializers.CharField()
    currentpassword = serializers.CharField()
    newpassword = serializers.CharField()

    def create(self, validated_data):
        """
        Create a new password.
        """

    def update(self, instance, validated_data):
        """
        Update a password.
        """
        # instance.userid = validated_data.get('userid', instance.userid)
        # instance.password = validated_data.get('hashedNewPassword', instance.password)
        # instance.save()
        # return instance

    def validate(self, attrs):
        """ check that userid and new password are different """
        if attrs["username"] == attrs["newpassword"]:
            raise serializers.ValidationError("username and new password should be different")
        return attrs

    def validate_password(self, value):
        """
        check if new password meets the specs
        min 1 lowercase and 1 uppercase alphabet
        1 number
        1 special character
        8-16 character length
        """

        if len(value) < 8 or len(value) > 16:
            raise serializers.ValidationError("It should be between 8 and 16 characters long")

        if not any(x.isupper() for x in value):
            raise serializers.ValidationError("It should have at least one upper case alphabet")

        if not any(x.islower() for x in value):
            raise serializers.ValidationError("It should have at least one lower case alphabet")

        if not any(x.isdigit() for x in value):
            raise serializers.ValidationError("It should have at least one number")

        valid_special_characters = {'@', '_', '!', '#', '$', '%', '^', '&', '*', '(', ')',
                                    '<', '>', '?', '/', '|', '{', '}', '~', ':'}

        if not any(x in valid_special_characters for x in value):
            raise serializers.ValidationError("It should have at least one special character")

        return value
