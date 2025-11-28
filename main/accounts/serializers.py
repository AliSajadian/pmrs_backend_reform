"""
Serializers for JWT-based authentication.

This module contains serializers for validation and data transformation:
- LoginSerializer1: Validate login credentials
- RegisterSerializer1: Validate user registration
- TokenRefreshSerializer1: Validate and refresh tokens
- ChangePasswordSerializer1: Validate password changes
- UserResponseSerializer: Format user data for responses

Serializers are kept focused on validation and data shaping only,
with no business logic (which belongs in services).
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

User = get_user_model()


class LoginSerializer1(serializers.Serializer):
    """
    Serializer for user login.
    Validates username and password fields only.
    """
    username = serializers.CharField(
        max_length=150,
        required=True,
        help_text="Username for authentication"
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Password for authentication"
    )

    def validate_username(self, value):
        """Validate username is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Username cannot be empty")
        return value.strip()

    def validate_password(self, value):
        """Validate password is not empty."""
        if not value:
            raise serializers.ValidationError("Password cannot be empty")
        return value

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class RegisterSerializer1(serializers.Serializer):
    """
    Serializer for user registration.
    Validates all required fields for creating a new user.
    """
    username = serializers.CharField(
        max_length=150,
        required=True,
        help_text="Unique username"
    )
    email = serializers.EmailField(
        required=True,
        help_text="Email address"
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Password (will be validated against Django's password validators)"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Password confirmation"
    )
    first_name = serializers.CharField(
        max_length=30,
        required=False,
        allow_blank=True,
        help_text="First name"
    )
    last_name = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        help_text="Last name"
    )
    personnel_code = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Personnel code"
    )

    def validate_username(self, value):
        """Check if username already exists."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        """Check if email already exists."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_password(self, value):
        """Validate password using Django's password validators."""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        """Check that passwords match."""
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({
                "password_confirm": "Passwords do not match"
            })
        return attrs

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class TokenRefreshSerializer1(serializers.Serializer):
    """
    Serializer for refreshing JWT tokens.
    Validates refresh token and returns new access and refresh tokens.
    """
    refresh_token = serializers.CharField(
        required=True,
        help_text="Refresh token to use for generating new tokens"
    )

    def validate_refresh_token(self, value):
        """Validate refresh token is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Refresh token cannot be empty")
        return value.strip()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ChangePasswordSerializer1(serializers.Serializer):
    """
    Serializer for changing user password.
    Validates old and new passwords.
    """
    old_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Current password"
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="New password"
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="New password confirmation"
    )

    def validate_new_password(self, value):
        """Validate new password using Django's password validators."""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        """Check that new passwords match and are different from old password."""
        if attrs.get('new_password') != attrs.get('new_password_confirm'):
            raise serializers.ValidationError({
                "new_password_confirm": "New passwords do not match"
            })
        
        if attrs.get('old_password') == attrs.get('new_password'):
            raise serializers.ValidationError({
                "new_password": "New password must be different from current password"
            })
        
        return attrs

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class UserResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for user data in responses.
    Formats user information for API responses.
    """
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'personnel_code',
            'is_active',
            'user_img',
            'date_joined',
            'last_login',
        ]
        read_only_fields = fields
    
    def get_full_name(self, obj):
        """Get user's full name."""
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class UserRoleResponseSerializer(serializers.Serializer):
    """
    Serializer for user role data in token claims.
    """
    role_id = serializers.IntegerField()
    role = serializers.CharField()
    project_id = serializers.IntegerField(allow_null=True)
    project_name = serializers.CharField(allow_null=True)
    all_projects = serializers.BooleanField()
    permissions = serializers.ListField(child=serializers.CharField())

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class LoginResponseSerializer(serializers.Serializer):
    """
    Serializer for login response data.
    """
    status = serializers.CharField(default='success')
    message = serializers.CharField(default='Login successful')
    user = UserResponseSerializer()
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    token_type = serializers.CharField(default='Bearer')
    access_expires_at = serializers.IntegerField()
    refresh_expires_at = serializers.IntegerField()
    roles = UserRoleResponseSerializer(many=True)
    all_permissions = serializers.ListField(child=serializers.CharField())
    is_admin = serializers.BooleanField()
    is_board = serializers.BooleanField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class TokenRefreshResponseSerializer(serializers.Serializer):
    """
    Serializer for token refresh response.
    """
    status = serializers.CharField(default='success')
    message = serializers.CharField(default='Token refreshed successfully')
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    token_type = serializers.CharField(default='Bearer')
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class LogoutResponseSerializer(serializers.Serializer):
    """
    Serializer for logout response.
    """
    status = serializers.CharField(default='success')
    message = serializers.CharField(default='Logout successful')

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ErrorResponseSerializer(serializers.Serializer):
    """
    Serializer for error responses.
    """
    status = serializers.CharField(default='error')
    message = serializers.CharField()
    errors = serializers.DictField(required=False)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
