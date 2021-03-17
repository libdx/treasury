import sys
from unittest import mock

import pytest
from django.conf import settings
from haversine import Unit, haversine

from project.apps.api.models import Treasure


@pytest.mark.parametrize(
    "radius, distance, is_found",
    (
        (10, 10 - 1, True),
        (10, 10 + 1, False),
        (2, 2 - 0.0001, True),
        (2, 2 + 0.0001, False),
        (2, 2 - sys.float_info.epsilon, True),
        (2, 2 + sys.float_info.epsilon, True),
        (2, 2 - 4 * sys.float_info.epsilon, True),
        (2, 2 + 4 * sys.float_info.epsilon, False),
    ),
)
def test_treasure_is_found(monkeypatch, radius, distance, is_found):
    monkeypatch.setattr(settings, "DEFAULT_TREASURE_HUNT_RADIUS", radius)
    treasure_mock = mock.Mock()

    assert Treasure.is_found(treasure_mock, distance) == is_found
