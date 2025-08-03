# core/mixins.py
from django.db import models
from django.utils import timezone

class TimestampMixin(models.Model):
    """Abstract model to add timestamp fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class UserOwnedMixin(models.Model):
    """Abstract model for user-owned objects"""
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='%(class)s_set'
    )
    
    class Meta:
        abstract = True
