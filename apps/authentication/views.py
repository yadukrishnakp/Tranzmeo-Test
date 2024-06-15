from typing import Any
from django.shortcuts import render
from rest_framework import generics, status
from apps.authentication.schemas import LoginPostSchema, LoginResponseSchema
from apps.authentication.serializers import LoginSerializer, LogoutSerializer
from apps.user.models import GeneratedAccessToken
from lat_and_long_core.helpers.helper import get_token_user_or_none
from lat_and_long_core.helpers.response import ResponseInfo
from lat_and_long_core.helpers.custom_messages import _account_tem_suspended, _invalid_credentials
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from django.contrib import auth
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework.permissions import IsAuthenticated
from lat_and_long_core.middleware.JWTAuthentication import BlacklistedJWTAuthentication
from django.utils import timezone




class LoginAPIView(generics.GenericAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(LoginAPIView, self).__init__(**kwargs)

    serializer_class = LoginPostSchema

    @swagger_auto_schema(tags=["Authorization"])
    def post(self, request):
        try:
            data = request.data
            email = data.get('email', '')
            password = data.get('password', '')
            # import pdb;pdb.set_trace()
            user = auth.authenticate(username=email, password=password)
            
            if user:
                serializer = LoginResponseSchema(user)

                if not user.is_active:
                    data = {'user': {}, 'token': '', 'refresh': ''}
                    self.response_format['status_code'] = status.HTTP_202_ACCEPTED
                    self.response_format["data"] = data
                    self.response_format["status"] = True
                    self.response_format["message"] = 'Account Temparary suspended, contact admin'
                    return Response(self.response_format, status=status.HTTP_200_OK)
                else:
                    refresh = RefreshToken.for_user(user)
                    data = {'user': serializer.data, 'token': str(
                        refresh.access_token), 'refresh': str(refresh)}
                    self.response_format['status_code'] = status.HTTP_200_OK
                    self.response_format["data"] = data
                    self.response_format["status"] = True
                    return Response(self.response_format, status=status.HTTP_200_OK)

            else:
                self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
                self.response_format["message"] = 'Invalid credentials'
                self.response_format["status"] = False
                return Response(self.response_format, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            pass
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status'] = False
            self.response_format['message'] = str(e)
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                
                
                
                
class LogoutApiView(generics.GenericAPIView):
    
    def __init__(self, **kwargs: Any):
        self.response_format = ResponseInfo().response
        super(LogoutApiView, self).__init__(**kwargs)
        
    serializer_class          = LogoutSerializer
    # permission_classes        = (IsAuthenticated,)
    authentication_classes    = [BlacklistedJWTAuthentication]

    
    @swagger_auto_schema(tags=["Authorization"])
    def post(self, request):
        
        try:
            user = get_token_user_or_none(request)
            if user is not None:
                GeneratedAccessToken.objects.using('reader').filter(user=user).delete()
                # update_last_logout(None, user)
            
            self.response_format['status'] = True
            self.response_format['status_code'] = status.HTTP_200_OK
            return Response(self.response_format, status=status.HTTP_200_OK)

        except Exception as e:
            self.response_format['status'] = False
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['message'] = str(e)
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
