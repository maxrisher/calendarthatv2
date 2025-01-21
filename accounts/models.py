from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    time_zone_name = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.email
