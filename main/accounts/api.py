"""
Thin API views for JWT authentication.

This module contains view classes that handle HTTP requests/responses only.
All business logic is delegated to service classes.

Views follow the thin view pattern:
1. Receive and validate HTTP request
2. Call appropriate service method
3. Format and return HTTP response
"""
import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from accounts.serializers import (
    LoginSerializer1,
    RegisterSerializer1,
    TokenRefreshSerializer1,
    ChangePasswordSerializer1,
    UserResponseSerializer,
)
from accounts.services import AuthService, UserService

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Extract client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_device_info(request):
    """Extract device information from request."""
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    return user_agent[:200]  # Limit length


class LoginAPIView(APIView):
    """
    API view for user login.
    
    POST /api/auth/login
    Body: {"username": "user", "password": "pass"}
    Returns: User data with JWT tokens
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer1

    def post(self, request):
        """Handle login request."""
        try:
            # Validate request data
            serializer = LoginSerializer1(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'status': 'error',
                    'message': 'Invalid input',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            # Extract validated data
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            # Get client info
            ip_address = get_client_ip(request)
            device_info = get_device_info(request)

            # Authenticate user (delegates to service)
            user, access_token, refresh_token, token_data = AuthService.authenticate_user(
                username=username,
                password=password,
                device_info=device_info,
                ip_address=ip_address
            )

            # Format response
            response_data = {
                'status': 'success',
                'message': 'Login successful',
                'user': UserResponseSerializer(user).data,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': token_data['token_type'],
                'access_expires_at': token_data['access_expires_at'],
                'refresh_expires_at': token_data['refresh_expires_at'],
                'roles': token_data['roles'],
                'all_permissions': token_data['all_permissions'],
                'is_admin': token_data['is_admin'],
                'is_board': token_data['is_board'],
            }

            logger.info("Successful login for user: %s", username)
            return Response(response_data, status=status.HTTP_200_OK)

        except ValidationError as e:
            logger.warning("Login validation error: %s", str(e))
            return Response({
                'status': 'error',
                'message': str(e.message) if hasattr(e, 'message') else str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            logger.error("Login error: %s", str(e), exc_info=True)
            return Response({
                'status': 'error',
                'message': 'An error occurred during login'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutAPIView(APIView):
    """
    API view for user logout.
    
    POST /api/auth/logout
    Body: {"refresh_token": "token", "logout_all": false}
    Returns: Success message
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Handle logout request."""
        user = request.user
        refresh_token = request.data.get('refresh_token')
        logout_all = request.data.get('logout_all', False)

        # Logout user (delegates to service)
        success = AuthService.logout_user(
            user=user,
            refresh_token=refresh_token,
            logout_all=logout_all
        )

        if success:
            message = 'Logged out from all devices' if logout_all else 'Logout successful'
            logger.info("User %s logged out", user.username)
            return Response({
                'status': 'success',
                'message': message
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'error',
                'message': 'Logout failed'
            }, status=status.HTTP_400_BAD_REQUEST)
                

class TokenRefreshAPIView(APIView):
    """
    API view for refreshing JWT tokens.
    
    POST /api/auth/refresh
    Body: {"refresh_token": "token"}
    Returns: New access and refresh tokens
    """
    permission_classes = [AllowAny]
    serializer_class = TokenRefreshSerializer1

    def post(self, request):
        """Handle token refresh request."""
        # Validate request data
        serializer = TokenRefreshSerializer1(data=request.data)
        if not serializer.is_valid():
            return Response({
                'status': 'error',
                'message': 'Invalid input',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        refresh_token = serializer.validated_data['refresh_token']

        # Refresh tokens (delegates to service)
        new_access_token, new_refresh_token = AuthService.refresh_tokens(refresh_token)

        response_data = {
            'status': 'success',
            'message': 'Token refreshed successfully',
            'access_token': new_access_token,
            'refresh_token': new_refresh_token,
            'token_type': 'Bearer'
        }

        logger.info("Token refreshed successfully")
        return Response(response_data, status=status.HTTP_200_OK)


class RegisterAPIView(APIView):
    """
    API view for user registration.
    
    POST /api/auth/register
    Body: {"username": "user", "email": "email@example.com", "password": "pass", ...}
    Returns: Created user data with JWT tokens
    """
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer1

    def post(self, request):
        """Handle registration request."""
        # Validate request data
        serializer = RegisterSerializer1(data=request.data)
        if not serializer.is_valid():
            return Response({
                'status': 'error',
                'message': 'Invalid input',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Extract validated data
        data = serializer.validated_data

        # Create user (delegates to service)
        user = UserService.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            personnel_code=data.get('personnel_code'),
            is_active=True
        )

        # Generate tokens for new user
        ip_address = get_client_ip(request)
        device_info = get_device_info(request)

        _, access_token, refresh_token, token_data = AuthService.authenticate_user(
            username=data['username'],
            password=data['password'],
            device_info=device_info,
            ip_address=ip_address
        )

        # Format response
        response_data = {
            'status': 'success',
            'message': 'Registration successful',
            'user': UserResponseSerializer(user).data,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer'
        }

        logger.info("New user registered: %s", user.username)
        return Response(response_data, status=status.HTTP_201_CREATED)


class ChangePasswordAPIView(APIView):
    """
    API view for changing user password.
    
    PUT /api/auth/changePassword
    Body: {"old_password": "old", "new_password": "new", "new_password_confirm": "new"}
    Returns: Success message
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer1

    def put(self, request):
        """Handle password change request."""
        # Validate request data
        serializer = ChangePasswordSerializer1(data=request.data)
        if not serializer.is_valid():
            return Response({
                'status': 'error',
                'message': 'Invalid input',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Extract validated data
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        # Change password (delegates to service)
        success = UserService.change_password(
            user_id=request.user.id,
            old_password=old_password,
            new_password=new_password
        )

        if success:
            logger.info("Password changed for user: %s", request.user.username)
            return Response({
                'status': 'success',
                'message': 'Password changed successfully. ' +
                'Please login again with your new password.'
            }, status=status.HTTP_200_OK)

        return Response({
                'status': 'error',
                'message': 'Password change failed'
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileAPIView(APIView):
    """
    API view for getting current user profile.
    
    GET /api/auth/profile
    Returns: Current user data
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get current user profile."""
        user = request.user
        user_data = UserResponseSerializer(user).data

        return Response({
            'status': 'success',
            'data': user_data
        }, status=status.HTTP_200_OK)
