"""
URL patterns for JWT authentication endpoints.

This module defines the URL routes for the new JWT-based authentication system.
These routes work alongside the existing Knox-based authentication.
"""
from django.urls import path

from accounts.api import (
    LoginAPIView,
    LogoutAPIView,
    TokenRefreshAPIView,
    RegisterAPIView,
    ChangePasswordAPIView,
    UserProfileAPIView,
)

urlpatterns = [
    # Authentication endpoints
    path('api/auth/login', LoginAPIView.as_view(), name='jwt-login'),
    path('api/auth/logout', LogoutAPIView.as_view(), name='jwt-logout'),
    path('api/auth/refresh', TokenRefreshAPIView.as_view(), name='jwt-refresh'),
    path('api/auth/register', RegisterAPIView.as_view(), name='jwt-register'),
    path('api/auth/changePassword', ChangePasswordAPIView.as_view(), name='jwt-change-password'),
    path('api/auth/profile', UserProfileAPIView.as_view(), name='jwt-profile'),
]

