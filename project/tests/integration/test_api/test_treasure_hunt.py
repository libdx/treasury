from unittest import mock

import pytest
from django.conf import settings
from haversine import Unit, haversine

import project.apps.api.tasks
from project.apps.api.models import Attempt, Treasure


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
        assert Attempt.objects.all().count() == 1
    elif status_code == 400:
        assert result["status"] == "error"
        assert result["distance"] == -1
        assert "error" in result


@pytest.mark.parametrize(
    "user_data, treasure_data, payload",
    (
        (
            {
                "username": "superuser",
                "password": "123",
                "email": "superuser@example.com",
            },
            {"latitude": 45.7597, "longitude": 4.8422},
            {"latitude": 48.8567, "longitude": 2.3508},
        ),
    ),
)
@pytest.mark.django_db
def test_authenticated_attempt(
    api_client, django_user_model, user_data, treasure_data, payload
):
    user = django_user_model.objects.create(**user_data)
    user.set_password(user_data["password"])
    user.save()

    Treasure.objects.create(**treasure_data)

    del user_data["email"]
    response = api_client.post("/api/auth/token/login/", user_data)

    assert response.status_code == 200
    token = response.json()["access"]

    api_client.credentials(HTTP_AUTHORIZATION="Bearer %s" % token)

    response = api_client.post("/api/treasure_hunt.json/", payload)

    assert response.status_code == 201
    result = response.json()
    treasure_location = (treasure_data["latitude"], treasure_data["longitude"])
    attempt_location = (payload["latitude"], payload["longitude"])
    distance = haversine(treasure_location, attempt_location, unit=Unit.METERS)
    assert result == {"status": "ok", "distance": distance}
    assert Attempt.objects.all().count() == 1
    assert Attempt.objects.first().user == user


def test_email_is_sent_once(api_client, db, monkeypatch):
    payload = {"latitude": 43.04, "longitude": 18.43, "email": "user@example.com"}

    Treasure.objects.create(latitude=43.04, longitude=18.43)

    send_email_mock = mock.Mock()
    monkeypatch.setattr(project.apps.api.tasks, "send_email", send_email_mock)

    response1 = api_client.post("/api/treasure_hunt.json/", payload)
    response2 = api_client.post("/api/treasure_hunt.json/", payload)

    assert response1.status_code == 201
    assert response2.status_code == 400

    send_email_mock.delay.assert_called_once()

    assert Attempt.objects.all().count() == 1
