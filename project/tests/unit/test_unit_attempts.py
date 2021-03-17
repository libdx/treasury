from unittest import mock

from haversine import Unit, haversine

from project.apps.api.models import Attempt


def test_distance():
    attempt_location = (23, 95)
    treasure_location = (150, 180)

    expected_distance = haversine(attempt_location, treasure_location, unit=Unit.METERS)

    attempt_mock = mock.Mock()
    treasure_mock = mock.Mock()

    attempt_mock.latitude = attempt_location[0]
    attempt_mock.longitude = attempt_location[1]

    treasure_mock.latitude = treasure_location[0]
    treasure_mock.longitude = treasure_location[1]

    actual_distance = Attempt.distance_to(attempt_mock, treasure_mock)

    assert actual_distance == expected_distance
