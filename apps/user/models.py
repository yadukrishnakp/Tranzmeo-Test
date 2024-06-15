
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django_acl.models import Group
from django_acl.utils.helper import acl_has_perms
from django_acl.models import AbstractDateFieldMix




class UserManager(BaseUserManager):
    def create_user(self, username, password = None, **extra_fields):
        if not username:
            raise ValueError(_('The username must be set'))

        user = self.model(username = username, **extra_fields)
        if password:
            user.set_password(password.strip())
            
        user.save()
        return user


    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('is_admin', True)
     
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff = True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser = True.'))
        
        return self.create_user(username, password, **extra_fields)



class Users(AbstractBaseUser, PermissionsMixin, AbstractDateFieldMix):
    class UserType(models.TextChoices):
        Rider   = 'Rider'
        Driver  = 'Driver'

    name                          = models.CharField(_('Name'), max_length = 300, blank = True, null = True)
    user_type                     = models.CharField(_('User Type'), max_length=100, choices=UserType.choices, null=True,blank=True)
    email                         = models.EmailField(_('email'), unique = True, max_length = 255, blank = True, null = True)
    username                      = models.CharField(_('username'), max_length = 300, blank = True, null = True)
    password                      = models.CharField(_('password'), max_length=255, blank = True, null = True)
    date_joined                   = models.DateTimeField(_('date_joined'),  auto_now_add = True, blank = True, null = True)
    is_verified                   = models.BooleanField(default = False)
    is_superuser                  = models.BooleanField(default = False)
    is_active                     = models.BooleanField(_('Is Active'), default=True)
    latitude                      = models.CharField(_('latitude'), max_length = 300, blank = True, null = True)
    longitude                     = models.CharField(_('longitude'), max_length = 300, blank = True, null = True)
    is_completed                  = models.BooleanField(default = False)
    
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['username']

    objects = UserManager()
    
    def __str__(self):
        return "{username}".format(username=self.username)
    
    def _password_has_been_changed(self):
        return self.original_password != self.password
    




class GeneratedAccessToken(AbstractDateFieldMix):
    token = models.TextField()
    user = models.ForeignKey(Users, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return self.token



    
    
