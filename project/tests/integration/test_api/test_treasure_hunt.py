import pytest
from haversine import Unit, haversine

from project.apps.api.models import Treasure


def test_get_treasure_hunt(api_client, db):
    """Tests treasure_hunt.json endpoint not allowed for GET."""
    response = api_client.get("/api/treasure_hunt.json/")

    assert response.status_code == 405


@pytest.mark.parametrize(
    "treasure_data, payload, status_code",
    (
        (
            {"latitude": 45.7597, "longitude": 4.8422},
            {"latitude": 48.8567, "longitude": 2.3508, "email": "user@example.com"},
            201,
        ),
        (
            {"latitude": 45.7597, "longitude": 4.8422},
            {
                "latitude": 48.8567,
                "longitude": 2.3508,
            },
            400,
        ),
        (
            {"latitude": 45.7597, "longitude": 4.8422},
            {"longitude": 2.3508, "email": "user@example.com"},
            400,
        ),
        (
            {"latitude": 45.7597, "longitude": 4.8422},
            {"latitude": 48.8567, "email": "user@example.com"},
            400,
        ),
        (
            {"latitude": 45.7597, "longitude": 4.8422},
            {},
            400,
        ),
    ),
)
def test_treasure_hunt_attempt(api_client, db, treasure_data, payload, status_code):
    Treasure.objects.create(**treasure_data)

    response = api_client.post("/api/treasure_hunt.json/", payload)

    assert response.status_code == status_code
    result = response.json()
    if status_code == 201:
        treasure_location = (treasure_data["latitude"], treasure_data["longitude"])
        attempt_location = (payload["latitude"], payload["longitude"])
        distance = haversine(treasure_location, attempt_location, unit=Unit.METERS)
        assert result == {"status": "ok", "distance": distance}
    elif status_code == 400:
        assert result["status"] == "error"
        assert result["distance"] == -1
        assert "error" in result
