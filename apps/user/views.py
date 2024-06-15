from rest_framework import generics,status, filters
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from apps.user.models import Users, Group
from apps.user.schemas import (
    RetrieveUserInfoApiSchema, 
    GetGroupDetailsApiSchema, 
    RetrieveRoleInfoResponseSchema, 
    RetrieveUsersSchema, 
    RetrievePermissionsResponceSchema,
)

from apps.user.serializers import (
    CreateOrUpdateGroupSerializer, 
    CreateOrUpdateRoleSerilizer, 
    CreateOrUpdateUserSerializer, 
    DestroyGropsRequestSerializer, 
    DestroyRoleRequestSerializer, 
    GetGroupDetailsRequestSerializer, 
    RetrieveGroupsSerializers, 
    RetrieveRoleInfoRequestSerializer, 
    RetrieveRolesSerializers, 
)


from lat_and_long_core.helpers.helper import get_object_or_none
from lat_and_long_core.helpers.response import ResponseInfo
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from lat_and_long_core.helpers.custom_messages import (
    _success, 
    _record_not_found,  
    _user_not_found,
)
from lat_and_long_core.helpers.pagination import RestPagination
from django_acl.models import Role
from lat_and_long_core.middleware.JWTAuthentication import BlacklistedJWTAuthentication
from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model
import os,sys



class CreateOrUpdateUserApiView(generics.GenericAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(CreateOrUpdateUserApiView, self).__init__(**kwargs)
        
    serializer_class = CreateOrUpdateUserSerializer
    # permission_classes = (IsAuthenticated,)
    
    @swagger_auto_schema(tags=["Users"])
    def post(self, request):
        try:

            serializer = self.serializer_class(data=request.data, context = {'request' : request})

            if not serializer.is_valid():
                self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
                self.response_format["status"] = False
                self.response_format["errors"] = serializer.errors
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

            user_instance = get_object_or_none(Users,pk=serializer.validated_data.get('user', None))

            serializer = self.serializer_class(user_instance, data=request.data, context = {'request' : request})
            if not serializer.is_valid():
                self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
                self.response_format["status"] = False
                self.response_format["errors"] = serializer.errors
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()
            
            self.response_format['status_code'] = status.HTTP_201_CREATED
            self.response_format["message"] = _success
            self.response_format["status"] = True
            return Response(self.response_format, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status'] = False
            self.response_format['message'] = f'exc_type : {exc_type},fname : {fname},tb_lineno : {exc_tb.tb_lineno},error : {str(e)}'
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
    


class GetAllUsersApiView(generics.ListAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(GetAllUsersApiView, self).__init__(**kwargs)
        
    queryset = Users.objects.all().exclude(is_superuser=True).order_by('-id')
    serializer_class = RetrieveUsersSchema
    # permission_classes = (IsAuthenticated,)
    pagination_class = RestPagination
    filter_backends    = [filters.SearchFilter]
    search_fields      = ['username','email',]
    
    @swagger_auto_schema(pagination_class=RestPagination, tags=["Users"])
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.serializer_class(page, many=True)
        return self.get_paginated_response(serializer.data)



class RetrievePermissionsApiView(generics.ListAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(RetrievePermissionsApiView, self).__init__(**kwargs)
        
    serializer_class          = RetrievePermissionsResponceSchema
    permission_classes        = (IsAuthenticated,)
    authentication_classes    = [BlacklistedJWTAuthentication]
    
    @swagger_auto_schema(tags=["Permission"])
    def get(self, request):

        try:
            
            permissions = Permission.objects.order_by('label').distinct('label')
            serializer = self.serializer_class(permissions, many=True, context={"request": request})
            
            user_instance = get_object_or_none(Users, pk=request.user.pk) 
            
            user_groups_field = get_user_model()._meta.get_field("user_groups")
            user_groups_query = "group__%s" % user_groups_field.related_query_name()
        
            roles = Role.objects.filter(**{user_groups_query: user_instance})
            
            active_permissions = set()
            for role in roles:
                role_permissions = role.permissions.all()
                for role_permission in role_permissions:
                    active_permissions.add(role_permission.pk)
    

            self.response_format['status_code'] = status.HTTP_200_OK
            data = {'permissions': serializer.data, 'active_permissions' : active_permissions }
            self.response_format["data"] = data
            self.response_format["status"] = True
            return Response(self.response_format, status=status.HTTP_200_OK)
            
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status'] = False
            self.response_format['message'] = f'exc_type : {exc_type},fname : {fname},tb_lineno : {exc_tb.tb_lineno},error : {str(e)}'
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 




class CreateOrUpdateRoleApiView(generics.GenericAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(CreateOrUpdateRoleApiView, self).__init__(**kwargs)
        
    serializer_class = CreateOrUpdateRoleSerilizer
    authentication_classes = [BlacklistedJWTAuthentication]
    permission_classes = (IsAuthenticated,)
    @swagger_auto_schema(tags=["Roles"])
    def post(self, request):
        try:
            
            role = request.data.get('role', None)
            if role is not None and role:
                role = get_object_or_none(Role,pk=role)
                if role is None:
                    self.response_format['status_code'] = status.HTTP_404_NOT_FOUND
                    self.response_format["message"] = _record_not_found
                    self.response_format["status"] = False
                    return Response(self.response_format, status=status.HTTP_404_NOT_FOUND)    
                
                serializer = self.serializer_class(role,data=request.data, context = {'request' : request})
            else:
                serializer = self.serializer_class(data=request.data, context = {'request' : request})
            
            
            if not serializer.is_valid():
                self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
                self.response_format["status"] = False
                self.response_format["errors"] = serializer.errors
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
            
            
            
            serializer.save()
            self.response_format['status_code'] = status.HTTP_201_CREATED
            self.response_format["message"] = _success
            self.response_format["status"] = True
            return Response(self.response_format, status=status.HTTP_201_CREATED)
            
        
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status'] = False
            self.response_format['message'] = f'exc_type : {exc_type},fname : {fname},tb_lineno : {exc_tb.tb_lineno},error : {str(e)}'
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 




class RetrieveRoleInfoApiView(generics.GenericAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(RetrieveRoleInfoApiView, self).__init__(**kwargs)
        
    serializer_class = RetrieveRoleInfoRequestSerializer

    role = openapi.Parameter('role', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True, description="Enter role id")
    
    @swagger_auto_schema(tags=["Roles"], manual_parameters=[role])
    def get(self, request):
        
        try:
            serializer = self.serializer_class(data=request.GET)
            
            
            if not serializer.is_valid():
                self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
                self.response_format["status"] = False
                self.response_format["errors"] = serializer.errors
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
            
            
            role = serializer.validated_data.get('role',None)
            if role is None:
                self.response_format['status_code'] = status.HTTP_404_NOT_FOUND
                self.response_format["status"] = False
                self.response_format["errors"] = serializer.errors
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
            
            
            
            data = { 'role': RetrieveRoleInfoResponseSchema(role, context={'request': request}).data}
            
            self.response_format['status_code'] = status.HTTP_200_OK
            self.response_format["data"] = data 
            self.response_format["message"] = _success
            self.response_format["status"] = True
            return Response(self.response_format, status=status.HTTP_200_OK)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status'] = False
            self.response_format['message'] = f'exc_type : {exc_type},fname : {fname},tb_lineno : {exc_tb.tb_lineno},error : {str(e)}'
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 





class RetrieveRolesApiView(generics.ListAPIView):
    
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(RetrieveRolesApiView, self).__init__(**kwargs)
        
    queryset = Role.objects.all().order_by('-id')
    serializer_class          = RetrieveRolesSerializers
    permission_classes        = (IsAuthenticated,)
    authentication_classes    = [BlacklistedJWTAuthentication]
    pagination_class          = RestPagination
    filter_backends           = [filters.SearchFilter]
    search_fields             = ['name',]
    
    
    @swagger_auto_schema(pagination_class=RestPagination, tags=["Roles"])
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.serializer_class(page, many=True)
        return self.get_paginated_response(serializer.data)
    
    
    


class DestroyRoleApiView(generics.GenericAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(DestroyRoleApiView, self).__init__(**kwargs)

    serializer_class = DestroyRoleRequestSerializer
    authentication_classes = [BlacklistedJWTAuthentication]
    permission_classes = (IsAuthenticated,)

    role = openapi.Schema('Destroy role record', in_=openapi.IN_BODY,required=['role'], properties={'role': openapi.Schema(type=openapi.TYPE_INTEGER)},type=openapi.TYPE_OBJECT)

    @swagger_auto_schema(tags=["Roles"], request_body=role)
    def delete(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():

                role = serializer.validated_data.get('role', None)
                role.delete()

                self.response_format['status_code'] = status.HTTP_200_OK
                self.response_format["message"] = _success
                self.response_format["status"] = True
                return Response(self.response_format, status=status.HTTP_200_OK)

            else:
                self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
                self.response_format["status"] = False
                self.response_format["errors"] = serializer.errors
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status'] = False
            self.response_format['message'] = f'exc_type : {exc_type},fname : {fname},tb_lineno : {exc_tb.tb_lineno},error : {str(e)}'
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        
        
        
class RetrieveGroupsApiView(generics.ListAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(RetrieveGroupsApiView, self).__init__(**kwargs)
        
        
    queryset                  = Group.objects.all().order_by('-id')
    serializer_class          = RetrieveGroupsSerializers
    permission_classes        = (IsAuthenticated,)
    authentication_classes    = [BlacklistedJWTAuthentication]
    pagination_class          = RestPagination
    filter_backends           = [filters.SearchFilter]
    search_fields             = ['name',]

    
    @swagger_auto_schema(pagination_class=RestPagination, tags=["Groups"])
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.serializer_class(page, many=True)
        return self.get_paginated_response(serializer.data)
    

class CreateOrUpdateGroupApiView(generics.GenericAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(CreateOrUpdateGroupApiView, self).__init__(**kwargs)
        
    serializer_class = CreateOrUpdateGroupSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BlacklistedJWTAuthentication]
    @swagger_auto_schema(tags=["Groups"])
    def post(self, request):
        try:
            group = request.data.get('group', None)
            if group is not None and group:
                group_instance = get_object_or_none(Group, pk=group) 
                if group_instance is not None:
                    serializer = self.serializer_class(group_instance,data=request.data, context = {'request' : request})
                else:
                    self.response_format['status_code'] = status.HTTP_404_NOT_FOUND
                    self.response_format["message"] = _record_not_found
                    self.response_format["status"] = False
                    return Response(self.response_format, status=status.HTTP_404_NOT_FOUND)    
            else:
                
                serializer = self.serializer_class(data=request.data, context = {'request' : request})
            
            
            if not serializer.is_valid():
                self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
                self.response_format["status"] = False
                self.response_format["errors"] = serializer.errors
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
            
            
            serializer.save()
            
            self.response_format['status_code'] = status.HTTP_201_CREATED
            self.response_format["message"] = _success
            self.response_format["status"] = True
            return Response(self.response_format, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status'] = False
            self.response_format['message'] = f'exc_type : {exc_type},fname : {fname},tb_lineno : {exc_tb.tb_lineno},error : {str(e)}'
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 





class RetrieveGroupInfoApiView(generics.GenericAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(RetrieveGroupInfoApiView, self).__init__(**kwargs)
        
    serializer_class = GetGroupDetailsRequestSerializer

    group = openapi.Parameter('group', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True, description="Enter group id")
    
    @swagger_auto_schema(tags=["Groups"], manual_parameters=[group])
    def get(self, request):
        
        try:
            serializer = self.serializer_class(data=request.GET)
            
            
            if not serializer.is_valid():
                self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
                self.response_format["status"] = False
                self.response_format["errors"] = serializer.errors
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
            
            group = serializer.validated_data.get('group',None)
            if group is None:
                self.response_format['status_code'] = status.HTTP_404_NOT_FOUND
                self.response_format["status"] = False
                self.response_format["errors"] = serializer.errors
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
                
            data = { 'group': GetGroupDetailsApiSchema(group, context={'request': request}).data }
            
            self.response_format['status_code'] = status.HTTP_200_OK
            self.response_format["data"] = data 
            self.response_format["message"] = _success
            self.response_format["status"] = True
            return Response(self.response_format, status=status.HTTP_200_OK)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status'] = False
            self.response_format['message'] = f'exc_type : {exc_type},fname : {fname},tb_lineno : {exc_tb.tb_lineno},error : {str(e)}'
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 


class DestroyGroupsApiView(generics.GenericAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(DestroyGroupsApiView, self).__init__(**kwargs)

    serializer_class = DestroyGropsRequestSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BlacklistedJWTAuthentication]
    group = openapi.Schema('Destroy group record', in_=openapi.IN_BODY,required=['group'], properties={'group': openapi.Schema(type=openapi.TYPE_INTEGER)},type=openapi.TYPE_OBJECT)

    @swagger_auto_schema(tags=["Groups"], request_body=group)
    def delete(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():

                group = serializer.validated_data.get('group', None)
                group.delete()

                self.response_format['status_code'] = status.HTTP_200_OK
                self.response_format["message"] = _success
                self.response_format["status"] = True
                return Response(self.response_format, status=status.HTTP_200_OK)

            else:
                self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
                self.response_format["status"] = False
                self.response_format["errors"] = serializer.errors
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status'] = False
            self.response_format['message'] = f'exc_type : {exc_type},fname : {fname},tb_lineno : {exc_tb.tb_lineno},error : {str(e)}'
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 



