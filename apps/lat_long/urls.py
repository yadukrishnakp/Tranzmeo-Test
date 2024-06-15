from django.urls import path, re_path, include
from . import views

urlpatterns = [
    re_path(r'^lat-long-calculations/', include([
        path('get-continues-path', views.GetContinuesPathApiView.as_view()),
        path('get-terrain-match', views.GetTerrainMatchingApiView.as_view()),
        path('get-list-all-points-terrains', views.GetListAllPointsTerrainApiView.as_view()),
        
    ])),

]