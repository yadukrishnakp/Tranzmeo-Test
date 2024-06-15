from rest_framework import serializers
from apps.user.models import Users
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.core.validators import validate_email


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField()
    
    class Meta:
        model  = Users
        fields = ['username', 'password']
        
        
        
        

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_message = {
        'bad_token': ('Token is expired or invalid')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):

        try:
            RefreshToken(self.token).blacklist()

        except TokenError:
            self.fail('bad_token')   


