from apps.user.models import Users
from rest_framework import serializers


class GetUserResponseSchemas(serializers.ModelSerializer):    
    class Meta:
        model  = Users
        fields = ['id', 'name', 'email', 'username', 'is_active', 'latitude', 'longitude']
    
    def to_representation(self, instance):
        datas = super().to_representation(instance)
        for key in datas.keys():
            try:
                if datas[key] is None:
                    datas[key] = ""
            except KeyError:
                pass
        return datas




