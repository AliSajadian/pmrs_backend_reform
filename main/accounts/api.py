"""
API views for the accounts application.

This module contains authentication and authorization endpoints including:
- User management (CRUD operations)
- Login/Register endpoints
- Permission and role management
- Group management
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from rest_framework import generics, viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from knox.models import AuthToken

from .serializers import UserSerializer, UserExSerializer, UserGroupSerializer, \
   GroupPermissionSerializer, UserPermissionSerializer, GroupSerializer, PermissionSerializer, \
   UserContractPermissionsSerializers,  ProjectConfirmersSerializers, RegisterSerializer, \
   LoginSerializer, PasswordSerializer
from .models import UserRole


class UserCreateAPI(generics.GenericAPIView):
    """
    Create a new user.
    """
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def post(self,request):
        """
        Create a new user.
        """
        user = get_user_model().objects.create(
                        username = request.data["username"],
                        first_name = request.data["first_name"],
                        last_name = request.data["last_name"],
                        email = request.data["email"],
                        is_active = request.data["is_active"],
                        )
        user.set_password(request.data["password"])
        user.save()
        serializer = UserExSerializer(user, context=self.get_serializer_context())
        return Response({"status": "success", "data": serializer.data},
                    status=status.HTTP_200_OK)


class UserDeleteAPI(generics.GenericAPIView):
    """
    Delete a user.
    """
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def delete(self, pk: int):
        """
        Delete a user.
        """
        user = get_user_model().objects.get(pk = pk)
        user.delete()

        return Response({"status": "success" }, status=status.HTTP_200_OK)


class UserGroupsExAPI(generics.RetrieveAPIView):
    """
    Get the user groups for a user.
    """
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, request, *args, **kwargs) -> Response:
        """
        Get the user groups for a user.
        """
        pk = kwargs.get('pk')
        user = get_user_model().objects.get(pk=pk)
        serializer = UserGroupSerializer(user)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, pk: int):
        """
        Update the user groups for a user.
        """
        user = get_user_model().objects.get(pk=pk)
        serializer = UserGroupSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": "success", "data": serializer.data},
                status=status.HTTP_200_OK
            )

        return Response(
            {"status": 'error', "data": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class GroupPermissionsExAPI(generics.RetrieveAPIView):
    """
    Get the group permissions for a group.
    """
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, request, *args, **kwargs) -> Response:
        """
        Get the group permissions for a group.
        """
        pk = kwargs.get('pk')
        group = Group.objects.get(pk=pk)
        serializer = GroupPermissionSerializer(group)
        return Response({"status": 'success', "data": serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, pk: int):
        """
        Update the group permissions for a group.
        """
        group = Group.objects.get(pk=pk)
        serializer = GroupPermissionSerializer(group, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": 'success', "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(
            {"status": 'error', "data": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


# User Permission
class UserPermissionsExAPI(generics.RetrieveAPIView):
    """
    Get the user permissions for a user.
    """
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, request, *args, **kwargs) -> Response:
        """
        Get the user permissions for a user.
        """
        pk = kwargs.get('pk')
        user = get_user_model().objects.get(pk=pk)
        serializer = UserPermissionSerializer(user)
        return Response({
            "status": 'success', "data": serializer.data}, 
            status=status.HTTP_200_OK
        )

    def put(self, request, pk):
        """
        Update the user permissions for a user.
        """
        user = get_user_model().objects.get(pk=pk)
        serializer = UserPermissionSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": 'success', "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(
            {"status": 'error', "data": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


#=========== Authorization Api ============
class UserAPI(viewsets.ModelViewSet):
    """
    Get the user for a user.
    """
    queryset = get_user_model().objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = UserExSerializer


class GroupAPI(viewsets.ModelViewSet):
    """
    Get the group for a group.
    """
    queryset = Group.objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = GroupSerializer


class PermissionAPI(viewsets.ModelViewSet):
    """
    Get the permission for a permission.
    """
    queryset = Permission.objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = PermissionSerializer


class UserGroupsAPI(viewsets.ModelViewSet):
    """
    Get the user groups for a user.
    """
    queryset = get_user_model().objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = UserGroupSerializer


class GroupPermissionsAPI(viewsets.ModelViewSet):
    """
    Get the group permissions for a group.
    """
    queryset = Group.objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = GroupPermissionSerializer


class UserPermissionsAPI(viewsets.ModelViewSet):
    """
    Get the user permissions for a user.
    """
    queryset = get_user_model().objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = UserPermissionSerializer


class UserExAPI(viewsets.ModelViewSet):
    """
    Get the user for a user.
    """
    queryset = get_user_model().objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = UserExSerializer


class ProjectConfirmersAPI(APIView):
    """
    Get the project confirmers for a contract.
    """
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, **kwargs):
        """
        Get the project confirmers for a contract.
        """
        contract_id = kwargs["contractid"]
        user_roles = UserRole.objects.filter(projectid__exact=contract_id)
        serializer = ProjectConfirmersSerializers(instance=(user_roles[0] \
            if len(user_roles) > 0 else None) if user_roles is not None else None, many=False)

        return Response({"status": 'success', "data": serializer.data},
                    status=status.HTTP_200_OK)


#=========== Authentication Api ============
class RegisterAPI(generics.GenericAPIView):
    """
    Register a new user.
    """
    serializer_class = RegisterSerializer

    def post(self, request):
        """
        Register a new user.
        """
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        _, token = AuthToken.objects.create(user)
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": token
        })

class LoginAPI(generics.GenericAPIView):
    """
    Login a user.
    """
    # serializer_class = LoginSerializer self.get_serializer
    def post(self, request, *args, **kwargs):
        """
        Login a user.
        """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        _, token = AuthToken.objects.create(user)

        user_roles = []
        user_contract_permissions_serializer = []
        user_roles = UserRole.objects.filter(userid__exact=user.id)
        # if(user_roles[0].all_projects == None or user_roles[0].all_projects == False):
        user_contract_permissions_serializer = UserContractPermissionsSerializers(
            instance=user_roles, many=True)
        # usergrouppermissions = []
        # usergroups = ()
        # for group in user.groups.all():
        #     if(group not in usergroups):
        #             usergroups.append(group.id)
        #     for permission in group.permissions.all():
        #         if(permission not in usergrouppermissions):
        #             usergrouppermissions.append(permission.codename)
        #
        # for permission in user.user_permissions.all():
        #     if(permission not in usergrouppermissions):
        #         usergrouppermissions.append(permission.codename)

        # if((1 not in usergroups) and (2 not in usergroups) and
        #   (usergroups == None or usergroups == [] or
        #   usergrouppermissions == None or usergrouppermissions == [])):
        #     # "دسترسی به سیستم به شما اختصاص داده نشده است، لطفا با راهبر سامانه تماس بگیرید."
        #     return Response({'error': 3})

        return Response({
                "status": "succeed", 
                "user": UserSerializer(user, context=self.get_serializer_context()).data, 
                "authToken": token,
                "userContractPermissions": user_contract_permissions_serializer.data \
                    if len(user_roles) > 0 else [],
            },
            status=status.HTTP_200_OK)


class LoginExAPI(generics.GenericAPIView):
    """
    Login a user.
    """
    def post(self, request):
        """
        Login a user.
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            # refresh = RefreshToken.for_user(user)
            # access_token = str(refresh.access_token)
            user = serializer.validated_data
            _, access_token = AuthToken.objects.create(user)

            response = Response({"user": user},
                                status=status.HTTP_200_OK)

            response.set_cookie(key="access_token",
                                value=access_token,
                                httponly=True,
                                secure=True,
                                samesite="None")

            response.set_cookie(key="refresh_token",
                                value=str(access_token),
                                httponly=True,
                                secure=True,
                                samesite="None")
            return response

        return Response({
                "status": "succeed", 
                "user": UserSerializer(user, context=self.get_serializer_context()).data, 
                "accessToken": access_token,
                "refreshToken": access_token,
            },
            status=status.HTTP_200_OK)


class PasswordAPIView(APIView):
    """
    Change the password for a user.
    """
    def get_object(self, userid):
        """
        Get the user object.
        """
        user = get_object_or_404(get_user_model(), id=userid)
        return user

    def put(self, request):
        """
        Change the password for a user.
        """
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            userid = serializer.data['userid']
            # username = serializer.data['username']
            user = self.get_object(userid)

            oldpassword = serializer.data['currentpassword']
            is_same_as_old = user.check_password(oldpassword)

            if not is_same_as_old:
                return Response({"password": ["You enter wrong password."]},
                                status=status.HTTP_400_BAD_REQUEST)

            new_password = serializer.data['newpassword']
            is_same_as_old = user.check_password(new_password)

            if is_same_as_old:
                return Response({"password": ["It should be different from your last password."]},
                                status=status.HTTP_400_BAD_REQUEST)

            # if user.username != username:
            #     user.username = username

            user.set_password(new_password)
            user.save()
            return Response({'success':True})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class LogoutAPI(APIView):

    # def post(self, request):
    #     refresh_token = request.COOKIES.get("refresh_token")

    #     if refresh_token:
    #         try:
                # refresh = RefreshToken(refresh_token)
                # refresh.blacklist()
        #     except Exception as e:
        #         return Response({"error":"Error invalidating token:" + str(e) },
        #                       status=status.HTTP_400_BAD_REQUEST)
        # response = Response({"message": "Successfully logged out!"}, status=status.HTTP_200_OK)
        # response.delete_cookie("access_token")
        # response.delete_cookie("refresh_token")

        # return response

# class CookieTokenRefreshAPI(TokenRefreshView):
    # def post(self, request):

    #     refresh_token = request.COOKIES.get("refresh_token")

    #     if not refresh_token:
    #         return Response({"error":"Refresh token not provided"},
    #                       status= status.HTTP_401_UNAUTHORIZED)

        # refresh = RefreshToken(refresh_token)
        # access_token = str(refresh.access_token)

        # response = Response({"message": "Access token token refreshed successfully"},
        #                     status=status.HTTP_200_OK)
        # response.set_cookie(key="access_token",
        #                     value=access_token,
        #                     httponly=True,
        #                     secure=True,
        #                     samesite="None")
        # return response
