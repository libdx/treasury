from unittest import mock

import pytest
from django.contrib.auth.models import User
from haversine import Unit, haversine

import project.apps.api.tasks
from project.apps.api.models import (
    _TREASURE_FOUND_BODY,
    _TREASURE_FOUND_SUBJECT,
    Attempt,
    Treasure,
)


def test_attempt_verify(monkeypatch, db):
    send_email_mock = mock.Mock()
    monkeypatch.setattr(project.apps.api.tasks, "send_email", send_email_mock)

    email = "magauser@example.com"

    user = User.objects.create(username="megauser", email=email)
    treasure = Treasure.objects.create(latitude=10, longitude=10)
    attempt = Attempt.objects.create(latitude=10, longitude=10, email=email)

    attempt.verify()

    assert attempt.treasure == treasure
    assert Attempt.objects.first().treasure == treasure
    assert Attempt.objects.first().user == user
    send_email_mock.delay.assert_called_once_with(
        (email,), subject=_TREASURE_FOUND_SUBJECT, body=_TREASURE_FOUND_BODY % 1
    )


@pytest.mark.django_db
def test_distance():
    attempt_location = (10, 15)
    treasure_location = (50, 88)

    expected_distance = haversine(attempt_location, treasure_location, unit=Unit.METERS)

    treasure = Treasure.objects.create(
        latitude=treasure_location[0], longitude=treasure_location[1]
    )

    attempt = Attempt.objects.create(
        email="user@example.com",
        latitude=attempt_location[0],
        longitude=attempt_location[1],
    )

    actual_distance = attempt.distance_to(treasure)

    assert actual_distance == expected_distance
