# Create your models here.

from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)  # For enabling/disabling category
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
