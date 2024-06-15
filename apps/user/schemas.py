from rest_framework import serializers
from apps.user.models import Users
from django_acl.models import Group, Role
from django.contrib.auth.models import Permission

from apps.user.serializers import GetGroupRolesOptionSerializer, PermissionSerializer



class RetrieveUsersSchema(serializers.ModelSerializer):

    class Meta:
        model = Users
        fields = ['pk','username','email','is_active', 'name', 'user_type']



class GetUserGroupsSerializer(serializers.ModelSerializer):
    
    value    =  serializers.IntegerField(source='pk')
    label    =  serializers.CharField(source='name')
    class Meta:
        model  = Permission
        fields = ['value','label']


class RetrieveUserInfoApiSchema(serializers.ModelSerializer):
    
    user_groups = serializers.SerializerMethodField('get_user_groups')
    class Meta:
        model = Users
        fields = ['username','email','is_password_reset_required','is_active','user_groups']
        
        
    def get_user_groups(self,obj):
        return GetUserGroupsSerializer(obj.user_groups.all(),many=True).data
    
    
    def to_representation(self, instance):
        datas = super().to_representation(instance)
        for key in datas.keys():
            try:
                if datas[key] is None:
                    datas[key] = ""
            except KeyError:
                pass
        return datas
    
class RetrieveRoleInfoResponseSchema(serializers.ModelSerializer):
    
    class Meta:
        model = Role
        fields = ['id','name','permissions']
    


class RetrievePermissionsResponceSchema(serializers.ModelSerializer):
    
    
    children = serializers.SerializerMethodField('get_children')
    value    =  serializers.CharField(source='label')
    class Meta:
        model  = Permission
        fields = ['label','value', 'children']
        
    
    def get_children(self, obj):
        permissions = Permission.objects.filter(label=obj.label).order_by('sub_label').distinct('sub_label')
        permission_serializer = PermissionSerializer(permissions, many=True)
        return permission_serializer.data
    
    

class GetGroupDetailsApiSchema(serializers.ModelSerializer):
    
    
    roles = serializers.SerializerMethodField('get_role')
    
    class Meta:
        model = Group
        fields = ['id','name','roles']
        

    def get_role(self, obj):
        return GetGroupRolesOptionSerializer(obj.roles.all(),many=True).data
