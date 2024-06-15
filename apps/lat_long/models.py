from django.db import models
from apps.user.models import Users
from django.utils.translation import gettext_lazy as _

# Create your models here.

class LatAndLongTerrain(models.Model):
    latitude          = models.CharField(_('Latitude'), max_length=256, null=True, blank=True)
    longitude         = models.CharField(_('Longitude'), max_length=256, null=True, blank=True)
    terrain           = models.CharField(_('Terrain'), max_length=256, null=True, blank=True)
    distance          = models.CharField(_('Terrain Distance'), max_length=256, null=True, blank=True)
    created_at        = models.DateTimeField(_('Created At'), auto_now_add=True, editable=False, blank=True, null=True)

    class Meta      : 
        verbose_name = 'LatAndLongTerrain'
        verbose_name_plural = "LatAndLongTerrains"

    def __str__(self):
        return str(self.created_at)