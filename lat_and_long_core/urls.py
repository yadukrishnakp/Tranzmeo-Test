"""
URL configuration for lat_and_long_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include,re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.views.generic import RedirectView

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings


schema_view             = get_schema_view(
        openapi.Info(
        title             = "Latitude and Longitude API",
        default_version   = 'v1',
        description       = "",
        terms_of_service  = "",
        contact           = openapi.Contact(email="yadukrishnakp007@gmail.com"),
    ),
    public               = True,
    permission_classes   = [permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', RedirectView.as_view(url='api/docs/',)),

    re_path(r'^api/',include([
        path('user/', include('apps.user.urls')),
        path('auth/', include('apps.authentication.urls')),
        path('lat-and-long/', include('apps.lat_long.urls')),
        
        re_path(r'^docs/', include([
            path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
            path("redoc", schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
                path('__debug__/', include('debug_toolbar.urls')),
        ])),
    ]))
]

urlpatterns += staticfiles_urlpatterns()   
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)