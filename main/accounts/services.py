"""
Business logic layer for the accounts application.

This module contains services that handle all business logic:
- AuthService: Authentication operations (login, logout, token refresh)
- UserService: User management (creation, updates, deactivation)
- TokenService: JWT token generation and management with Redis
- PermissionService: Permission and role management

Following the fat services pattern, all business logic is centralized here,
keeping views thin and focused on HTTP concerns only.
"""
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.core.cache import caches
from django.core.exceptions import ValidationError
from django.db import transaction, models
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError

from accounts.models import UserRole, Role, RolePermission, Permission

User = get_user_model()
logger = logging.getLogger(__name__)


class PermissionService:
    """
    Service for handling user permissions and roles.
    Provides methods to retrieve and check user permissions.
    """
    
    @staticmethod
    def get_user_roles_and_permissions(user: User) -> Dict[str, Any]:
        """
        Get all roles and permissions for a user across all projects.
        
        Args:
            user: User instance
            
        Returns:
            Dictionary containing roles, permissions, and flags
        """
        try:
            user_roles = UserRole.objects.filter(userid=user).select_related(
                'roleid', 'projectid'
            ).prefetch_related('roleid__role_rolepermission__permissionid')
            
            roles_data = []
            all_permissions = set()
            is_admin = False
            is_board = False
            
            for user_role in user_roles:
                # Get permissions for this role
                role_permissions = RolePermission.objects.filter(
                    roleid=user_role.roleid
                ).select_related('permissionid')
                
                permissions_list = [
                    rp.permissionid.permission 
                    for rp in role_permissions 
                    if rp.permissionid and rp.permissionid.permission
                ]
                
                all_permissions.update(permissions_list)
                
                # Check if user is admin or board member
                role_name_lower = str(user_role.roleid.role).lower()
                if 'admin' in role_name_lower:
                    is_admin = True
                if 'board' in role_name_lower:
                    is_board = True
                
                role_data = {
                    'role_id': user_role.roleid.roleid,
                    'role': str(user_role.roleid.role),
                    'project_id': user_role.projectid.contractid if user_role.projectid else None,
                    'project_name': str(user_role.projectid.contract) if user_role.projectid else None,
                    'all_projects': user_role.all_projects if user_role.all_projects is not None else False,
                    'permissions': permissions_list
                }
                roles_data.append(role_data)
            
            return {
                'roles': roles_data,
                'all_permissions': list(all_permissions),
                'is_admin': is_admin,
                'is_board': is_board,
                'has_roles': len(roles_data) > 0
            }
            
        except Exception as e:
            logger.error(f"Error getting user roles and permissions: {str(e)}")
            return {
                'roles': [],
                'all_permissions': [],
                'is_admin': False,
                'is_board': False,
                'has_roles': False
            }
    
    @staticmethod
    def check_user_permission(user: User, permission_name: str, project_id: Optional[int] = None) -> bool:
        """
        Check if user has a specific permission.
        
        Args:
            user: User instance
            permission_name: Permission name to check
            project_id: Optional project ID to check permission for specific project
            
        Returns:
            True if user has the permission, False otherwise
        """
        try:
            # Get user roles
            user_roles_query = UserRole.objects.filter(userid=user)
            
            # Filter by project if specified
            if project_id is not None:
                user_roles_query = user_roles_query.filter(
                    models.Q(projectid_id=project_id) | models.Q(all_projects=True)
                )
            
            # Get all role IDs for the user
            role_ids = user_roles_query.values_list('roleid', flat=True)
            
            # Check if any of these roles have the required permission
            has_permission = RolePermission.objects.filter(
                roleid__in=role_ids,
                permissionid__permission=permission_name
            ).exists()
            
            return has_permission
            
        except Exception as e:
            logger.error(f"Error checking user permission: {str(e)}")
            return False
    
    @staticmethod
    def get_project_confirmers(project_id: int) -> Dict[str, str]:
        """
        Get confirmers for all permission types in a project.
        
        Args:
            project_id: Project/Contract ID
            
        Returns:
            Dictionary mapping permission types to confirmer names
        """
        try:
            user_roles = UserRole.objects.filter(projectid_id=project_id).first()
            
            if not user_roles:
                return {}
            
            # Get confirmers for each permission type
            confirmers = {
                'financial_info': user_roles.financialInfo_confirmor(),
                'hse': user_roles.hse_confirmor(),
                'progress_state': user_roles.progressState_confirmor(),
                'time_progress_state': user_roles.timeProgressState_confirmor(),
                'invoice': user_roles.invoice_confirmor(),
                'financial_invoice': user_roles.financialInvoice_confirmor(),
                'work_volume': user_roles.workVolume_confirmor(),
                'pms_progress': user_roles.pmsProgress_confirmor(),
                'budget': user_roles.budget_confirmor(),
                'machinary': user_roles.machinary_confirmor(),
                'project_personel': user_roles.projectPersonel_confirmor(),
                'problem': user_roles.problem_confirmor(),
                'critical_action': user_roles.criticalAction_confirmor(),
                'project_dox': user_roles.projectDox_confirmor(),
                'periodic_dox': user_roles.periodicDox_confirmor(),
                'zone_image': user_roles.zoneImage_confirmor(),
            }
            
            return confirmers
            
        except Exception as e:
            logger.error(f"Error getting project confirmers: {str(e)}")
            return {}


class TokenService:
    """
    Service for JWT token generation and management with Redis storage.
    Handles token creation with custom claims, storage, and revocation.
    """
    
    REDIS_CACHE_ALIAS = 'tokens'
    REFRESH_TOKEN_PREFIX = 'refresh_token'
    ACCESS_TOKEN_PREFIX = 'access_token'
    BLACKLIST_PREFIX = 'blacklist'
    USER_TOKENS_PREFIX = 'user_tokens'
    
    @classmethod
    def generate_tokens_for_user(
        cls, 
        user: User,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Tuple[str, str, Dict[str, Any]]:
        """
        Generate access and refresh tokens with custom claims for a user.
        
        Args:
            user: User instance
            device_info: Optional device information
            ip_address: Optional IP address
            
        Returns:
            Tuple of (access_token, refresh_token, token_data)
        """
        try:
            # Get user roles and permissions
            roles_data = PermissionService.get_user_roles_and_permissions(user)
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            # Add custom claims to both tokens
            custom_claims = {
                'user_id': user.id,
                'username': str(user.username),
                'email': str(user.email) if user.email else '',
                'full_name': f"{user.first_name} {user.last_name}".strip(),
                'personnel_code': user.personnel_code,
                'roles': roles_data['roles'],
                'all_permissions': roles_data['all_permissions'],
                'is_admin': roles_data['is_admin'],
                'is_board': roles_data['is_board'],
            }
            
            # Add custom claims to refresh token
            for key, value in custom_claims.items():
                refresh[key] = value
            
            # Generate access token from refresh token
            access = refresh.access_token
            
            # Store refresh token in Redis
            cls._store_refresh_token(
                user_id=user.id,
                token_jti=str(refresh['jti']),
                token=str(refresh),
                device_info=device_info,
                ip_address=ip_address
            )
            
            token_data = {
                'access_token': str(access),
                'refresh_token': str(refresh),
                'access_expires_at': access['exp'],
                'refresh_expires_at': refresh['exp'],
                'token_type': 'Bearer',
                **custom_claims
            }
            
            logger.info(f"Generated tokens for user {user.username}")
            return str(access), str(refresh), token_data
            
        except Exception as e:
            logger.error(f"Error generating tokens for user: {str(e)}")
            raise
    
    @classmethod
    def refresh_access_token(cls, refresh_token: str) -> Tuple[str, str]:
        """
        Generate a new access token from a refresh token.
        
        Args:
            refresh_token: Refresh token string
            
        Returns:
            Tuple of (new_access_token, new_refresh_token)
        """
        try:
            # Validate refresh token
            refresh = RefreshToken(refresh_token)
            user_id = refresh['user_id']
            token_jti = str(refresh['jti'])
            
            # Check if token is in Redis
            if not cls._is_token_valid(user_id, token_jti):
                raise TokenError("Token not found or has been revoked")
            
            # Revoke old refresh token
            cls._revoke_token(user_id, token_jti)
            
            # Generate new tokens
            user = User.objects.get(id=user_id)
            new_access, new_refresh, _ = cls.generate_tokens_for_user(user)
            
            logger.info(f"Refreshed tokens for user {user.username}")
            return new_access, new_refresh
            
        except TokenError as e:
            logger.warning(f"Invalid refresh token: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            raise
    
    @classmethod
    def revoke_user_token(cls, user_id: int, token_jti: str) -> bool:
        """
        Revoke a specific token for a user.
        
        Args:
            user_id: User ID
            token_jti: JWT ID (jti claim)
            
        Returns:
            True if token was revoked, False otherwise
        """
        return cls._revoke_token(user_id, token_jti)
    
    @classmethod
    def revoke_all_user_tokens(cls, user_id: int) -> int:
        """
        Revoke all tokens for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of tokens revoked
        """
        try:
            cache = caches[cls.REDIS_CACHE_ALIAS]
            
            # Get all token JTIs for this user
            user_tokens_key = f"{cls.USER_TOKENS_PREFIX}:{user_id}"
            token_jtis = cache.get(user_tokens_key, set())
            
            # Revoke each token
            count = 0
            for token_jti in token_jtis:
                if cls._revoke_token(user_id, token_jti):
                    count += 1
            
            # Clear the user tokens set
            cache.delete(user_tokens_key)
            
            logger.info(f"Revoked {count} tokens for user {user_id}")
            return count
            
        except Exception as e:
            logger.error(f"Error revoking all user tokens: {str(e)}")
            return 0
    
    @classmethod
    def _store_refresh_token(
        cls,
        user_id: int,
        token_jti: str,
        token: str,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> bool:
        """Store refresh token in Redis with metadata."""
        try:
            cache = caches[cls.REDIS_CACHE_ALIAS]
            
            # Store token with metadata
            token_key = f"{cls.REFRESH_TOKEN_PREFIX}:{user_id}:{token_jti}"
            token_data = {
                'token': token,
                'user_id': user_id,
                'device_info': device_info,
                'ip_address': ip_address,
                'created_at': datetime.utcnow().isoformat(),
                'last_used': datetime.utcnow().isoformat(),
            }
            
            # Set with 7 days expiration (matching refresh token lifetime)
            cache.set(token_key, token_data, timeout=60 * 60 * 24 * 7)
            
            # Add to user's token set
            user_tokens_key = f"{cls.USER_TOKENS_PREFIX}:{user_id}"
            user_tokens = cache.get(user_tokens_key, set())
            user_tokens.add(token_jti)
            cache.set(user_tokens_key, user_tokens, timeout=60 * 60 * 24 * 7)
            
            return True
            
        except Exception as e:
            logger.error(f"Error storing refresh token: {str(e)}")
            return False
    
    @classmethod
    def _is_token_valid(cls, user_id: int, token_jti: str) -> bool:
        """Check if token exists in Redis and is not blacklisted."""
        try:
            cache = caches[cls.REDIS_CACHE_ALIAS]
            
            # Check if token exists
            token_key = f"{cls.REFRESH_TOKEN_PREFIX}:{user_id}:{token_jti}"
            token_data = cache.get(token_key)
            
            if not token_data:
                return False
            
            # Check if token is blacklisted
            blacklist_key = f"{cls.BLACKLIST_PREFIX}:{user_id}:{token_jti}"
            is_blacklisted = cache.get(blacklist_key)
            
            return not is_blacklisted
            
        except Exception as e:
            logger.error(f"Error checking token validity: {str(e)}")
            return False
    
    @classmethod
    def _revoke_token(cls, user_id: int, token_jti: str) -> bool:
        """Revoke a token by adding it to blacklist and removing from storage."""
        try:
            cache = caches[cls.REDIS_CACHE_ALIAS]
            
            # Add to blacklist
            blacklist_key = f"{cls.BLACKLIST_PREFIX}:{user_id}:{token_jti}"
            cache.set(blacklist_key, True, timeout=60 * 60 * 24 * 7)
            
            # Remove from storage
            token_key = f"{cls.REFRESH_TOKEN_PREFIX}:{user_id}:{token_jti}"
            cache.delete(token_key)
            
            # Remove from user tokens set
            user_tokens_key = f"{cls.USER_TOKENS_PREFIX}:{user_id}"
            user_tokens = cache.get(user_tokens_key, set())
            user_tokens.discard(token_jti)
            cache.set(user_tokens_key, user_tokens, timeout=60 * 60 * 24 * 7)
            
            return True
            
        except Exception as e:
            logger.error(f"Error revoking token: {str(e)}")
            return False


class AuthService:
    """
    Service for authentication operations.
    Handles login, logout, and token refresh logic.
    """
    
    @staticmethod
    def authenticate_user(
        username: str, 
        password: str,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Tuple[User, str, str, Dict[str, Any]]:
        """
        Authenticate user and generate tokens.
        
        Args:
            username: Username
            password: Password
            device_info: Optional device information
            ip_address: Optional IP address
            
        Returns:
            Tuple of (user, access_token, refresh_token, token_data)
            
        Raises:
            ValidationError: If authentication fails
        """
        try:
            # Get user
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist as e:
                logger.warning(f"Login attempt for non-existent user: {username}")
                raise ValidationError("Invalid username or password") from e
            
            # Check if user is active
            if not user.is_active:
                logger.warning(f"Login attempt for inactive user: {username}")
                raise ValidationError("User account is disabled")
            
            # Verify password
            if not user.check_password(password):
                logger.warning(f"Failed login attempt for user: {username}")
                raise ValidationError("Invalid username or password")
            
            # Generate tokens
            access_token, refresh_token, token_data = TokenService.generate_tokens_for_user(
                user=user,
                device_info=device_info,
                ip_address=ip_address
            )
            
            logger.info(f"Successful login for user: {username}")
            return user, access_token, refresh_token, token_data
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error during authentication: {str(e)}")
            raise ValidationError("Authentication failed")
    
    @staticmethod
    def logout_user(user: User, refresh_token: Optional[str] = None, logout_all: bool = False) -> bool:
        """
        Logout user by revoking tokens.
        
        Args:
            user: User instance
            refresh_token: Optional refresh token to revoke (for single device logout)
            logout_all: If True, revoke all tokens for user (all devices)
            
        Returns:
            True if logout was successful
        """
        try:
            if logout_all:
                # Revoke all user tokens
                count = TokenService.revoke_all_user_tokens(user.id)
                logger.info(f"Logged out user {user.username} from all devices ({count} tokens)")
                return True
            elif refresh_token:
                # Revoke specific token
                try:
                    refresh = RefreshToken(refresh_token)
                    token_jti = str(refresh['jti'])
                    success = TokenService.revoke_user_token(user.id, token_jti)
                    logger.info(f"Logged out user {user.username} from single device")
                    return success
                except TokenError:
                    logger.warning(f"Invalid refresh token during logout for user {user.username}")
                    return False
            else:
                logger.warning(f"Logout called without refresh token or logout_all flag")
                return False
                
        except Exception as e:
            logger.error(f"Error during logout: {str(e)}")
            return False
    
    @staticmethod
    def refresh_tokens(refresh_token: str) -> Tuple[str, str]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Refresh token string
            
        Returns:
            Tuple of (new_access_token, new_refresh_token)
            
        Raises:
            ValidationError: If refresh token is invalid
        """
        try:
            return TokenService.refresh_access_token(refresh_token)
        except TokenError as e:
            logger.warning(f"Token refresh failed: {str(e)}")
            raise ValidationError("Invalid or expired refresh token")
        except Exception as e:
            logger.error(f"Error refreshing tokens: {str(e)}")
            raise ValidationError("Token refresh failed")


class UserService:
    """
    Service for user management operations.
    Handles user creation, updates, and role assignment.
    """
    
    @staticmethod
    @transaction.atomic
    def create_user(
        username: str,
        email: str,
        password: str,
        first_name: str = '',
        last_name: str = '',
        personnel_code: Optional[int] = None,
        is_active: bool = True,
    ) -> User:
        """
        Create a new user.
        
        Args:
            username: Username
            email: Email address
            password: Password
            first_name: First name
            last_name: Last name
            personnel_code: Personnel code
            is_active: Is user active
            
        Returns:
            Created user instance
            
        Raises:
            ValidationError: If user creation fails
        """
        try:
            # Check if username already exists
            if User.objects.filter(username=username).exists():
                raise ValidationError("Username already exists")
            
            # Check if email already exists
            if email and User.objects.filter(email=email).exists():
                raise ValidationError("Email already exists")
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                personnel_code=personnel_code,
                is_active=is_active,
            )
            
            logger.info(f"Created user: {username}")
            return user
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise ValidationError("User creation failed")
    
    @staticmethod
    @transaction.atomic
    def update_user(
        user_id: int,
        **kwargs
    ) -> User:
        """
        Update user information.
        
        Args:
            user_id: User ID
            **kwargs: Fields to update
            
        Returns:
            Updated user instance
            
        Raises:
            ValidationError: If update fails
        """
        try:
            user = User.objects.get(id=user_id)
            
            # Update allowed fields
            allowed_fields = [
                'first_name', 'last_name', 'email', 
                'personnel_code', 'is_active', 'user_img'
            ]
            
            for field, value in kwargs.items():
                if field in allowed_fields:
                    setattr(user, field, value)
            
            user.save()
            logger.info(f"Updated user: {user.username}")
            return user
            
        except User.DoesNotExist as e:
            raise ValidationError("User not found") from e
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            raise ValidationError("User update failed")
    
    @staticmethod
    @transaction.atomic
    def change_password(
        user_id: int,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        Change user password.
        
        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password
            
        Returns:
            True if password was changed successfully
            
        Raises:
            ValidationError: If password change fails
        """
        try:
            user = User.objects.get(id=user_id)
            
            # Verify old password
            if not user.check_password(old_password):
                raise ValidationError("Current password is incorrect")
            
            # Check if new password is same as old
            if user.check_password(new_password):
                raise ValidationError("New password must be different from current password")
            
            # Set new password
            user.set_password(new_password)
            user.save()
            
            # Revoke all tokens (force re-login)
            TokenService.revoke_all_user_tokens(user_id)
            
            logger.info(f"Changed password for user: {user.username}")
            return True
            
        except User.DoesNotExist as e:
            raise ValidationError("User not found") from e
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            raise ValidationError("Password change failed")
    
    @staticmethod
    def deactivate_user(user_id: int) -> bool:
        """
        Deactivate a user and revoke all their tokens.
        
        Args:
            user_id: User ID
            
        Returns:
            True if user was deactivated successfully
        """
        try:
            user = User.objects.get(id=user_id)
            user.is_active = False
            user.save()
            
            # Revoke all tokens
            TokenService.revoke_all_user_tokens(user_id)
            
            logger.info(f"Deactivated user: {user.username}")
            return True
            
        except User.DoesNotExist:
            logger.warning(f"Attempted to deactivate non-existent user: {user_id}")
            return False
        except Exception as e:
            logger.error(f"Error deactivating user: {str(e)}")
            return False

