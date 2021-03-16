import sys

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from haversine import Unit, haversine

from project.apps.api import tasks

_TREASURE_FOUND_SUBJECT = "Treasure found, congratulations!"

_TREASURE_FOUND_BODY = (
    "Hey, you’ve found a treasure, congratulations!"
    "You are %s treasure hunter who has found the treasure."
)

_TREASURE_NOT_DEFINED_ERROR = "Treasure not defined."


class Treasure(models.Model):
    """Treasure model with geo coordinates."""

    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def is_found(self, distance):
        """Checks is treasure within the min radius by comparing it with `distance`."""
        eps = sys.float_info.epsilon
        radius = settings.DEFAULT_TREASURE_HUNT_RADIUS
        return (distance + eps) <= radius or (distance - eps) <= radius

    def found_times(self):
        return 1


class Attempt(models.Model):
    """Represents user's attempt to find treasure."""

    user = models.ForeignKey(
        User,
        related_name="attempts",
        on_delete=models.CASCADE,
        null=True,
    )
    treasure = models.ForeignKey(
        Treasure,
        related_name="attempts",
        on_delete=models.CASCADE,
        null=True,
    )
    email = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    @receiver(pre_save, sender="api.Attempt")
    def _pre_save(sender, instance, *args, **kwargs):
        instance.treasure = Treasure.objects.latest("created_at")

    def verify(self):
        """Verifies attempt and if it is close enough to treasure
        sends congratulation email.
        """
        self.treasure = Treasure.objects.latest("created_at")
        if not self.treasure:
            raise ValueError(_TREASURE_NOT_DEFINED_ERROR)

        distance = self.distance_to(self.treasure)
        if self.treasure.is_found(distance):
            tasks.send_email(
                (self.email,),
                subject=_TREASURE_FOUND_SUBJECT,
                body=_TREASURE_FOUND_BODY % 1,
            )
        return distance

    def distance_to(self, treasure):
        """Calculates distance to treasure."""
        treasure_location = (treasure.latitude, treasure.longitude)
        attempt_location = (self.latitude, self.longitude)

        return haversine(treasure_location, attempt_location, unit=Unit.METERS)
