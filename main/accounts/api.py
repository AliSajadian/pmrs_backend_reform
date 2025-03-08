from rest_framework import generics, viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from knox.models import AuthToken
import re

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

from .models import *
from .serializers import *

# User 
class UserCreateAPI(generics.GenericAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ] 

    def post(self,request):
        try:
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
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserDeleteAPI(generics.GenericAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ] 

    def delete(self, request, pk, format=None):
        try:
            user = get_user_model().objects.get(pk = pk)
            user.delete()

            return Response({"status": "success" }, status=status.HTTP_200_OK)         
        except Exception as e:
            return Response({"status": "error", "data": str(e) }, status=status.HTTP_400_BAD_REQUEST) 

    # User Group
class UserGroupsExAPI(generics.RetrieveAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ] 

    def get(self, request, pk=None, format=None):
        try:
            user = get_user_model().objects.get(pk=pk)
            serializer = UserGroupSerializer(user)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": 'error', "data": str(e)}, status=status.HTTP_400_BAD_REQUEST) 

    def put(self, request, pk, format=None):
        try:
            user = get_user_model().objects.get(pk=pk)
            serializer = UserGroupSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"status": 'error', "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"status": 'error', "data": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Group Permission
class GroupPermissionsExAPI(generics.RetrieveAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ] 

    def get(self, request, pk, format=None):
        try:
            group = Group.objects.get(pk=pk)
            serializer = GroupPermissionSerializer(group)
            return Response({"status": 'success', "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": 'error', "data": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        group = Group.objects.get(pk=pk)
        serializer = GroupPermissionSerializer(group, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": 'success', "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"status": 'error', "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

# User Permission
class UserPermissionsExAPI(generics.RetrieveAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ] 

    def get(self, request, pk, format=None):
        try:
            user = get_user_model().objects.get(pk=pk)
            serializer = UserPermissionSerializer(user)
            return Response({"status": 'success', "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": 'error', "data": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        user = get_user_model().objects.get(pk=pk)
        serializer = UserPermissionSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": 'success', "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"status": 'error', "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

#=========== Authorization Api ============
class UserAPI(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = UserExSerializer
  
class GroupAPI(viewsets.ModelViewSet):
    queryset = Group.objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = GroupSerializer

class PermissionAPI(viewsets.ModelViewSet):
    queryset = Permission.objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = PermissionSerializer

class UserGroupsAPI(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = UserGroupSerializer

class GroupPermissionsAPI(viewsets.ModelViewSet):
    queryset = Group.objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = GroupPermissionSerializer

class UserPermissionsAPI(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = UserPermissionSerializer

class UserExAPI(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = UserExSerializer

class ProjectConfirmersAPI(APIView):
    permission_classes = [
        permissions.IsAuthenticated
    ] 

    def get(self, request, *args, **kwargs):
        try:
            contractId = kwargs["contractid"]  
            userRoles = UserRole.objects.filter(projectid__exact=contractId)
            serializer = ProjectConfirmersSerializers(instance=(userRoles[0] if len(userRoles) > 0 else None) if userRoles is not None else None, many=False)
            return Response({"status": 'success', "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": 'error', "data": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            

#=========== Authentication Api ============
class RegisterAPI(generics.GenericAPIView):
  serializer_class = RegisterSerializer

  def post(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    _, token = AuthToken.objects.create(user)
    return Response({
      "user": UserSerializer(user, context=self.get_serializer_context()).data,
      "token": token
    })

class LoginAPI(generics.GenericAPIView):
    # serializer_class = LoginSerializer self.get_serializer
    def post(self, request, *args, **kwargs):
        try:
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data
            _, token = AuthToken.objects.create(user)
            
            user_roles = []
            userContractPermissionsSerializer = []
            user_roles = UserRole.objects.filter(userid__exact=user.id)
            # if(user_roles[0].all_projects == None or user_roles[0].all_projects == False):
            userContractPermissionsSerializer = UserContractPermissionsSerializers(user_roles, many=True)
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

            # if((1 not in usergroups) and (2 not in usergroups) and (usergroups == None or usergroups == [] or usergrouppermissions == None or usergrouppermissions == [])):
            #     # "دسترسی به سیستم به شما اختصاص داده نشده است، لطفا با راهبر سامانه تماس بگیرید."
            #     return Response({'error': 3})
            
            return Response({
                    "status": "succeed", 
                    "user": UserSerializer(user, context=self.get_serializer_context()).data, 
                    "authToken": token,
                    "userContractPermissions": userContractPermissionsSerializer.data if len(user_roles) > 0 else [],
                }, 
                status=status.HTTP_200_OK) 

        except Exception as e:
            return Response({"status": 'error: unauthorized', "data": str(e)}, status=status.HTTP_401_UNAUTHORIZED)  

class LoginExAPI(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        try:
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data
 
            return Response({
                    "status": "succeed", 
                }, 
                status=status.HTTP_200_OK) 

        except Exception as e:
            return Response({"status": 'error: unauthorized', "data": str(e)}, status=status.HTTP_401_UNAUTHORIZED)  

class PasswordAPIView(APIView):
    def get_object(self, userid):
        user = get_object_or_404(get_user_model(), id=userid)
        return user

    def put(self, request):
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            userid = serializer.data['userid']
            username = serializer.data['username']
            user = self.get_object(userid)
            oldpassword = serializer.data['currentpassword']
            is_same_as_old = user.check_password(oldpassword)
            if (not is_same_as_old):
                """
                old password and new user passwords should be the same
                """
                return Response({"password": ["You enter wrong password."]},
                                status=status.HTTP_400_BAD_REQUEST)            
            new_password = serializer.data['newpassword']
            is_same_as_old = user.check_password(new_password)
            if is_same_as_old:
                """
                old password and new passwords should not be the same
                """
                return Response({"password": ["It should be different from your last password."]},
                                status=status.HTTP_400_BAD_REQUEST)
            # if user.username != username:
            #     user.username = username
            user.set_password(new_password)
            user.save()
            return Response({'success':True})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   



       
