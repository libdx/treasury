import sys

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save
from django.dispatch import receiver
from haversine import Unit, haversine

from project.apps.api import tasks
from project.apps.api.exceptions import (
    SuccessfulAttemptExistsError,
    TreasureNotDefinedError,
)

_TREASURE_FOUND_SUBJECT = "Treasure found, congratulations!"

_TREASURE_FOUND_BODY = (
    "Hey, you’ve found a treasure, congratulations! "
    "You are %s treasure hunter who has found the treasure."
)


class Treasure(models.Model):
    """Treasure model with geo coordinates."""

    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "lat=%s, long=%s" % (self.latitude, self.longitude)

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

    def __str__(self):
        return "%s (lat=%s, long=%s)" % (self.email, self.latitude, self.longitude)

    @staticmethod
    @receiver(pre_save, sender="api.Attempt")
    def _pre_save(sender, instance, *args, **kwargs):
        """Ensure attempt is in consistent state before save."""
        instance.treasure = instance.treasure or Treasure.objects.latest("created_at")
        instance.user = (
            instance.user or User.objects.filter(email=instance.email).first()
        )

    def _other_earlier_successful_attempts(self):
        """Returns `QuerySet` of successful attempts for all users.

        Attempts are scoped by `self.treasure` and are in ascending order.
        """
        return Attempt.objects.order_by("updated_at").filter(
            Q(updated_at__lt=self.updated_at) & Q(treasure=self.treasure)
        )

    def _last_successful_attempt(self):
        """Returns last successful attempt for attemp's user or None.

        Attempt is scoped by `self.email` and `self.treasure`.
        """
        return Attempt.objects.filter(Q(successful=True) & Q(email=self.email))

    def verify(self):
        """Verifies attempt and if it is close enough to treasure
        sends congratulation email.
        """
        if not self.treasure:
            raise TreasureNotDefinedError()

        if self._last_successful_attempt():
            raise SuccessfulAttemptExistsError()

        distance = self.distance_to(self.treasure)
        if self.treasure.is_found(distance):
            self.successful = True
            self.save()

            current_attempt_number = (
                self._other_earlier_successful_attempts().count() + 1
            )

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
