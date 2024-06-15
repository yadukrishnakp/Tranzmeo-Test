from django.shortcuts import render
from apps.lat_long.models import LatAndLongTerrain
from apps.lat_long.serializers import LatLongFileUploadSerializer, TerrainMatchingSerializer
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from lat_and_long_core.helpers.helper import calculate_distance_terrain, calculate_distances
from lat_and_long_core.helpers.pagination import RestPagination
from lat_and_long_core.helpers.response import ResponseInfo
from rest_framework import generics
import sys, os
from django.db.models import Q
from lat_and_long_core.helpers.custom_messages import _success
import pandas as pd
import numpy as np
import csv

# Create your views here.


# 
class GetContinuesPathApiView(generics.GenericAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(GetContinuesPathApiView, self).__init__(**kwargs)
    
    serializer_class          = LatLongFileUploadSerializer
    
    @swagger_auto_schema(tags=["Lat and Long"])
    def post(self, request):
        try:
            
            serializer = self.serializer_class(data=request.data, context = {'request' : request})
            if not serializer.is_valid():
                self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
                self.response_format["status"] = False
                self.response_format["errors"] = serializer.errors
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
            
            file_result = serializer.validated_data['file']
            df = pd.read_csv(file_result)

            df['distance'] = [0] + calculate_distances(df)

            threshold = 5 * np.median(df['distance'])  
            outliers = df['distance'] > threshold

            for i in range(1, len(df) - 1):
                if outliers[i]:
                    df.loc[i, 'latitude'] = (df.loc[i-1, 'latitude'] + df.loc[i+1, 'latitude']) / 2
                    df.loc[i, 'longitude'] = (df.loc[i-1, 'longitude'] + df.loc[i+1, 'longitude']) / 2

            df = df.drop(columns=['distance'])

            df.to_csv('corrected_latitude_longitude_details.csv', index=False)

            self.response_format['status_code'] = status.HTTP_201_CREATED
            self.response_format["message"] = _success
            self.response_format["status"] = True
            return Response(self.response_format, status=status.HTTP_201_CREATED)
                
        
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status'] = False
            self.response_format['message'] = str(e)
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetTerrainMatchingApiView(generics.GenericAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(GetTerrainMatchingApiView, self).__init__(**kwargs)
    
    serializer_class          = TerrainMatchingSerializer
    
    @swagger_auto_schema(tags=["Lat and Long"])
    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data, context = {'request' : request})
            if not serializer.is_valid():
                self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
                self.response_format["status"] = False
                self.response_format["errors"] = serializer.errors
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
            
            file_result = serializer.validated_data['file']
            df = pd.read_csv(file_result)

            terrain_data = pd.read_csv('terrain_classification_test.csv')
            
            cumulative_distance = [0]
            for i in range(1, len(df)):
                dist = calculate_distance_terrain(df.loc[i-1, 'latitude'], df.loc[i-1, 'longitude'],
                                        df.loc[i, 'latitude'], df.loc[i, 'longitude'])
                cumulative_distance.append(cumulative_distance[-1] + dist)
            df['cumulative_distance'] = cumulative_distance

            def get_terrain(distance):
                for index, row in terrain_data.iterrows():
                    if distance < row['distance (in km)']:
                        return terrain_data.iloc[index - 1]['terrain'] if index > 0 else terrain_data.iloc[0]['terrain']
                return terrain_data.iloc[-1]['terrain']

            df['terrain'] = df['cumulative_distance'].apply(get_terrain)

            for index, row in df.iterrows():
                LatAndLongTerrain.objects.create(
                    latitude=row['latitude'],
                    longitude=row['longitude'],
                    terrain=row['terrain'],
                    distance=row['cumulative_distance']
                )

            df.to_csv('latitude_longitude_with_terrain.csv', index=False)

            self.response_format['status_code'] = status.HTTP_201_CREATED
            self.response_format["message"] = _success
            self.response_format["status"] = True
            return Response(self.response_format, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status'] = False
            self.response_format['message'] = str(e)
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
class GetListAllPointsTerrainApiView(generics.GenericAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(GetListAllPointsTerrainApiView, self).__init__(**kwargs)
    
    # serializer_class    = RideDetailsOrListingSchema
    pagination_class    = RestPagination
  
  
    @swagger_auto_schema(tags=["Lat and Long"], pagination_class=RestPagination)
    def get(self, request):
        
        try:

            # Filtering points with 'road' in terrain and without 'civil station'
            points_with_road = LatAndLongTerrain.objects.filter(terrain__contains='road')
            filtered_points = []
            for point in points_with_road:
                terrain_list = [terrain.strip() for terrain in point.terrain.split(',')]
                if 'road' in terrain_list and 'civil station' not in terrain_list:
                    filtered_points.append({
                        'latitude': point.latitude,
                        'longitude': point.longitude,
                        'terrain': point.terrain,
                        'distance': point.distance,
                        'created_at': point.created_at
                    })

            # Write the filtered points to a new CSV file
            file_path = 'filtered_terrain_points.csv'
            with open(file_path, 'w', newline='') as csvfile:
                fieldnames = ['latitude', 'longitude', 'terrain', 'distance', 'created_at']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for point in filtered_points:
                    writer.writerow(point)
            
     
            self.response_format['status_code'] = status.HTTP_201_CREATED
            self.response_format["message"] = _success
            self.response_format["status"] = True
            self.response_format["data"] = filtered_points
            return Response(self.response_format, status=status.HTTP_201_CREATED)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status'] = False
            self.response_format['message'] = f'exc_type : {exc_type},fname : {fname},tb_lineno : {exc_tb.tb_lineno},error : {str(e)}'
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 