from django.contrib import admin

from apps.user.models import GeneratedAccessToken,Users


# Register your models here.



@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('email','username','name','is_superuser','is_verified','is_active', )
    list_display_links = ['email']
    search_fields = ('email','username', )
    list_filter = ('created_date', 'is_active', )
    
    
    









@admin.register(GeneratedAccessToken)
class GeneratedAccessTokenAdmin(admin.ModelAdmin):
    list_display = ('token','user')
    list_filter  = ('user',)
    
    
