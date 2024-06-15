from apps.lat_long.models import LatAndLongTerrain
from apps.user.models import Users
from rest_framework import serializers
from lat_and_long_core.helpers.helper import get_object_or_none

class LatLongFileUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)

    def validate(self, attrs):
        return super().validate(attrs)
    

class TerrainMatchingSerializer(serializers.Serializer):
    file      = serializers.FileField(required=True)

    def validate(self, attrs):
        return super().validate(attrs)
    

class ListAllPointsTerrainSerializer(serializers.Serializer):
    file      = serializers.FileField(required=True)
    name      = serializers.CharField(required=True)
    distance  = serializers.CharField(required=True)

    class Meta:
        model =  LatAndLongTerrain
        fields = ['file','name','distance']   

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):  

        request                   = self.context.get('request')
        instance                  = LatAndLongTerrain()
        instance.name             = validated_data.get('name')
        instance.distance         = validated_data.get('distance')
        instance.save()
        return instance
    