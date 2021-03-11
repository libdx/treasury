import sys

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from haversine import Unit, haversine


class Treasure(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def is_found(self, distance):
        eps = sys.float_info.epsilon
        radius = settings.DEFAULT_TREASURE_HUNT_RADIUS
        return (distance + eps) <= radius or (distance - eps) <= radius


class Attempt(models.Model):
    user = models.ForeignKey(
        User, related_name="attempts", on_delete=models.CASCADE, null=True
    )
    email = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def distance_to(self, treasure):
        treasure_location = (treasure.latitude, treasure.longitude)
        attempt_location = (self.latitude, self.longitude)

        return haversine(treasure_location, attempt_location, unit=Unit.METERS)
