from django.contrib.auth.models import User
from django.db import models


class Attempt(models.Model):
    user = models.ForeignKey(
        User, related_name="attempts", on_delete=models.CASCADE, null=True
    )
    email = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
