"""
URLs for the accounts application.

This module contains the URLs for the accounts application.
"""
from rest_framework import routers
from django.urls import path, include
from knox import views as knox_views

from .api import *
       
router = routers.DefaultRouter()
router.register('api/auth/users', UserAPI, 'users')
router.register('api/auth/groups', GroupAPI, 'groups')
router.register('api/auth/usergroups', UserGroupsAPI, 'usergroups')
router.register('api/auth/permissions', PermissionAPI, 'permissions')
router.register('api/auth/grouppermissions', GroupPermissionsAPI, 'grouppermissions')

urlpatterns = [
    path('api/auth', include('knox.urls')),
    path('api/auth/loginEx', LoginExAPI.as_view()),
    path('api/auth/login', LoginAPI.as_view()),
    # path("api/auth/logout/", LogoutAPI.as_view(), name="user-logout"),
    # path("api/auth/refresh/", CookieTokenRefreshAPI.as_view(), name="token-refresh"),
    path("api/auth/changePassword", PasswordAPIView.as_view(), name="changePassword"),
    path('api/contractConfirmers/<int:contractid>/', ProjectConfirmersAPI.as_view(), name='contractConfirmers'),
]

urlpatterns += router.urls

