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
    path('api/auth/', LoginExAPI.as_view()),
    path('api/auth/login', LoginAPI.as_view()),
    path("api/auth/changePassword", PasswordAPIView.as_view(), name="changePassword"),
    path('api/contractConfirmers/<int:contractid>/', ProjectConfirmersAPI.as_view(), name='contractConfirmers'),
]

urlpatterns += router.urls