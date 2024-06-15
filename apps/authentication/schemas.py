from rest_framework import serializers
from apps.user.models import Users




class LoginPostSchema(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['email','password']

class LoginResponseSchema(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['email','username', 'is_active', 'is_verified', 'is_superuser']

