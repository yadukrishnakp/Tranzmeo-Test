from django.urls import path
from . import views


urlpatterns = [
    
    path('login', views.LoginAPIView.as_view()),
    path('logout', views.LogoutApiView.as_view()),
]