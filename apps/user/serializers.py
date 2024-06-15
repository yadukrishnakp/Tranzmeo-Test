import re
from uuid import uuid4
from rest_framework import serializers
from django.contrib.auth.models import Permission
from apps.user.models import  Users
from django_acl.models import Group, Role
from django.contrib.auth.hashers import check_password
import datetime
from django.utils.translation import gettext_lazy as _
from lat_and_long_core.helpers.helper import get_object_or_none
from django.contrib.auth.hashers import check_password




class NullableDateField(serializers.DateField):
    def to_internal_value(self, data):
        if data == '':
            return None
        else:
            return super().to_internal_value(data)



class CreateOrUpdateUserSerializer(serializers.ModelSerializer):
    user                      = serializers.IntegerField(allow_null=True, required=False)
    username                  = serializers.CharField(required=True)
    name                      = serializers.CharField(required=True)
    email                     = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    password                  = serializers.CharField(required=False)
    is_active                 = serializers.BooleanField(default=False)
    user_type                 = serializers.ChoiceField(choices=Users.UserType.choices,required=False)

    class Meta:
        model = Users 
        fields = ['user', 'username', 'name', 'email', 'password', 'is_active', 'user_type']
    
    
    def validate(self, attrs):
        email           = attrs.get('email', '')
        user            = attrs.get('user', None)
        username        = attrs.get('username', None)
        
        user_query_set = Users.objects.filter(email=email)
        user_object    = Users.objects.filter(username=username)

        if username is not None:
            if not re.match("^[a-zA-Z0-9._@]*$", username):
                raise serializers.ValidationError({'username':("Enter a valid Username. Only alphabets, numbers, '@', '_', and '.' are allowed.")})
            
        if user is not None:
            user_instance = get_object_or_none(Users,pk=user)
            user_query_set = user_query_set.exclude(pk=user_instance.pk)
            user_object    = user_object.exclude(pk=user_instance.pk)
        
        if user_object.exists():
            raise serializers.ValidationError({"username":('Username already exists!')})
        
        if user_query_set.exists():
            raise serializers.ValidationError({"email":('Email already exists!')})
        
        
            
        return super().validate(attrs)

    

    def create(self, validated_data):
        password                  = validated_data.get('password')
        
        instance                  = Users()
        instance.username         = validated_data.get('username')
        instance.email            = validated_data.get('email')
        instance.name             = validated_data.get('name')
        instance.user_type        = validated_data.get('user_type')
        instance.set_password(password) 
        instance.is_active        = validated_data.get('is_active')
        instance.save()
        
        return instance

    
    def update(self, instance, validated_data):
        
        password = validated_data.get('password','')
        instance.username   = validated_data.get('username')
        instance.email      = validated_data.get('email')
        instance.name       = validated_data.get('name')
        instance.user_type  = validated_data.get('user_type')

        if password:
            instance.set_password(password) 

        if validated_data.get('is_active',''):
            instance.is_active = validated_data.get('is_active')
        instance.save()
                
        return instance

    



        
        

class CreateOrUpdateRoleSerilizer(serializers.ModelSerializer):
    role = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=255, required=True)
    permissions = serializers.PrimaryKeyRelatedField(many=True, queryset=Permission.objects.all())
    
    class Meta:
        model = Role
        fields = ['role','name','permissions']
        
 
    def validate(self, attrs):
        role = attrs.get('role')
        name = attrs.get('name')
        role_query_set = Role.objects.filter(name=name)
        if role is not None:
            role_query_set = role_query_set.exclude(pk=role)
        
        if role_query_set.exists():
            raise serializers.ValidationError({"name": ['Name already exists!']})   
        return super().validate(attrs)
    
        
    def create(self, validated_data):
        
        instance = Role()
        instance.name = validated_data.get('name')
        instance.save() 
        
        permissions = validated_data.get('permissions')
        if instance is not None:
            permission_instance = get_object_or_none(Role, pk=instance.pk)
            if permission_instance is not None:
                instance.permissions.clear()
                for permission in permissions:
                    permission_instance.permissions.add(permission)
            
        return instance
    
    
    def update(self, instance, validated_data):
        
        instance.name = validated_data.get('name')
        permissions = validated_data.get('permissions')
        instance.save()
        instance.permissions.clear()
        permission_instance = get_object_or_none(Role, pk=instance.pk)
        
        if permission_instance is not None:
            permission_instance.permissions.clear()
            for permission in permissions:
                permission_instance.permissions.add(permission)
        
        return instance
    
    
    
class RetrieveRoleInfoRequestSerializer(serializers.ModelSerializer):
    role = serializers.IntegerField(read_only=False, required=True)
    
    def validate(self, attrs):
        role_id = attrs.get('role')
        role    = Role.objects.filter(id=role_id).first()
        if role:
            attrs['role'] = role
        else:
            raise serializers.ValidationError({"role": [f"Invalid pk \"{role_id}\" - object does not exist."]})
        
        
        return super().validate(attrs)
    class Meta:
        model = Role
        fields = ['role']
    



class GetPermissionsSerializer(serializers.ModelSerializer):
    
    value    =  serializers.IntegerField(source='pk')
    label    =  serializers.CharField(source='name')
    class Meta:
        model  = Permission
        fields = ['value','label']


class PermissionSerializer(serializers.ModelSerializer):
    
    
    children = serializers.SerializerMethodField('get_children')
    value    =  serializers.SerializerMethodField('get_label')
    label    =  serializers.CharField(source='sub_label')
    class Meta:
        model  = Permission
        fields = ['label','value', 'children']
        
        
    def get_children(self, obj):
        permissions = Permission.objects.filter(label=obj.label).filter(sub_label=obj.sub_label)
        permission_serializer = GetPermissionsSerializer(permissions, many=True)
        return permission_serializer.data
    
    
    def get_label(self, obj):
        return "{}".format(uuid4())
        


class RetrieveRolesSerializers(serializers.ModelSerializer):
    
    permissions = serializers.SerializerMethodField('get_permissions')
    
    class Meta:
        model = Role
        fields = ['id','name','permissions']
        
        
    def get_permissions(self, obj):
        permissions = [name for name in obj.permissions.values_list('name', flat=True)]
        return permissions
    
    
    def to_representation(self, instance):
        datas = super().to_representation(instance)
        for key in datas.keys():
            try:
                if datas[key] is None:
                    datas[key] = ""
            except KeyError:
                pass
        return datas
    
    
    
class DestroyRoleRequestSerializer(serializers.ModelSerializer):
    role = serializers.IntegerField(read_only=False, required=True)
    
    
    def validate(self, attrs):
        
        role_id = attrs.get('role')
        role    = Role.objects.filter(id=role_id).first()
        if role:
            attrs['role'] = role
        else:
            raise serializers.ValidationError({"role": [f"Invalid pk \"{role_id}\" - object does not exist."]}) 
        
        
        return super().validate(attrs)
    class Meta:
        model = Role
        fields = ['role']
        
        
        

class RetrieveGroupsSerializers(serializers.ModelSerializer):
    
    
    roles = serializers.SerializerMethodField('get_roles')
    class Meta:
        model = Group
        fields = ['pk','name','roles']
        
        
    def get_roles(self, obj):
        roles = [name for name in obj.roles.values_list('name', flat=True)]
        return roles
    
        
    def to_representation(self, instance):
        datas = super().to_representation(instance)
        for key in datas.keys():
            try:
                if datas[key] is None:
                    datas[key] = ""
            except KeyError:
                pass
        return datas
    
    
    
    
class CreateOrUpdateGroupSerializer(serializers.ModelSerializer):
    
    group = serializers.IntegerField(read_only=False, required=False)
    name = serializers.CharField(max_length=255, required=True)
    roles = serializers.PrimaryKeyRelatedField(read_only=False, many=True, queryset=Role.objects.all())
    
    class Meta:
        model = Group
        fields = ['group','name','roles']
        
 
    def validate(self, attrs):
        group = attrs.get('group')
        name  = attrs.get('name')
        group_query_set = Group.objects.filter(name=name)
        if group is not None:
            group_query_set = group_query_set.exclude(pk=group)
        
        if group_query_set.exists():
            raise serializers.ValidationError({"name": ['Name already exists!']})   
        
        return super().validate(attrs)
        
        
        
    def create(self, validated_data):
        instance = Group()
        instance.name = validated_data.get('name')
        instance.save()
        
        roles = validated_data.pop('roles')

        
        if instance is not None:
            role_instance = get_object_or_none(Group, pk=instance.pk)
            if role_instance is not None:
                role_instance.roles.clear()
                for role in roles:
                    role_instance.roles.add(role)
            
        return instance
    
        
    def update(self, instance, validated_data):
        
        instance.name = validated_data.get('name')
        instance.save()
        
        
        roles = validated_data.pop('roles')
        
        if instance is not None:
            role_instance = get_object_or_none(Group, pk=instance.pk)
            if role_instance is not None:
                role_instance.roles.clear()
                for role in roles:
                    role_instance.roles.add(role)
            
        return instance
    
    
class GetGroupRolesOptionSerializer(serializers.ModelSerializer):
    
    value    =  serializers.IntegerField(source='pk')
    label    =  serializers.CharField(source='name')
    class Meta:
        model  = Permission
        fields = ['value','label']

# class GetGroupDetailsRequestSerializer(serializers.ModelSerializer):
#     group = serializers.PrimaryKeyRelatedField(read_only=False, queryset=Group.objects.all(), required=True)
#     class Meta:
#         model = Group
#         fields = ['group']
    
class GetGroupDetailsRequestSerializer(serializers.ModelSerializer):
    group = serializers.IntegerField(read_only=False)

    def validate(self, attrs):
        group_id = attrs.get('group')
        group    = Group.objects.filter(id=group_id).first()
        if group:
            attrs['group'] = group
        else:
            raise serializers.ValidationError({"group": [f"Invalid pk \"{group_id}\" - object does not exist."]}) 
        
        return super().validate(attrs)
        
    class Meta:
        model = Group
        fields = ['group']
        

class DestroyGropsRequestSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(read_only=False, queryset=Group.objects.all())
    class Meta:
        model = Group
        fields = ['group']
        
        
        
