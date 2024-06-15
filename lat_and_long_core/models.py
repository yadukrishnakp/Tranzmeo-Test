from django.db import models
from safedelete import SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel
from django.utils.translation import gettext_lazy as _
from django_acl.models import AbstractDateFieldMix
from apps.user.models import Users

class AbstractDateTimeFieldBaseModel(SafeDeleteModel, AbstractDateFieldMix):
    _safedelete_policy = SOFT_DELETE_CASCADE
    
    created_by    = models.ForeignKey(Users, on_delete=models.SET_NULL, related_name='%(class)s_created', null=True, blank=True)
    modified_by   = models.ForeignKey(Users, on_delete=models.SET_NULL, related_name='%(class)s_modified', null=True, blank=True)
    is_active     = models.BooleanField(default=True)
    
    class Meta:
        abstract = True
