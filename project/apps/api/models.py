import sys

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
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
    successful = models.BooleanField(default=False)
    email = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    @receiver(pre_save, sender="api.Attempt")
    def _pre_save(sender, instance, *args, **kwargs):
        """Ensure attempt is in consistent state before save."""
        instance.treasure = instance.treasure or Treasure.objects.latest("created_at")
        instance.user = (
            instance.user or User.objects.filter(email=instance.email).first()
        )

    def _earlier_successful_attempts(self):
        """Returns list of successful attempts.

        Attemps are scoped by `self.treasure` and are in ascending order.
        """
        return Attempt.objects.order_by("updated_at").filter(
            Q(updated_at__lt=self.updated_at) & Q(treasure=self.treasure)
        )

    def verify(self):
        """Verifies attempt and if it is close enough to treasure
        sends congratulation email.
        """
        self.treasure = Treasure.objects.latest("created_at")
        if not self.treasure:
            raise ValueError(_TREASURE_NOT_DEFINED_ERROR)

        distance = self.distance_to(self.treasure)
        if self.treasure.is_found(distance):
            self.successful = True
            self.save()

            current_attempt_number = self._earlier_successful_attempts().count() + 1

            tasks.send_email.delay(
                (self.email,),
                subject=_TREASURE_FOUND_SUBJECT,
                body=_TREASURE_FOUND_BODY % (current_attempt_number),
            )
        return distance

    def distance_to(self, treasure):
        """Calculates distance to treasure."""
        treasure_location = (treasure.latitude, treasure.longitude)
        attempt_location = (self.latitude, self.longitude)

        return haversine(treasure_location, attempt_location, unit=Unit.METERS)
