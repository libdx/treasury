import pytest


@pytest.mark.parametrize(
    "payload, status_code",
    (
        (
            {
                "username": "superuser",
                "password": "123",
                "email": "superuser@examplee.com",
            },
            201,
        ),
        ({"username": "superuser", "password": "123"}, 400),
        ({"username": "superuser"}, 400),
        ({"password": "123"}, 400),
        ({}, 400),
    ),
)
def test_register(api_client, db, payload, status_code):
    """Tests user registration."""
    response = api_client.post("/api/auth/register/", payload)

    result = response.json()
    assert response.status_code == status_code
    if status_code == 201:
        assert result["username"] == payload["username"]


@pytest.mark.parametrize(
    "user_data, payload",
    (
        (
            {
                "username": "superuser",
                "password": "123",
                "email": "superuser@example.com",
            },
            {
                "username": "superuser",
                "password": "456",
                "email": "goodman@example.com",
            },
        ),
        (
            {
                "username": "superuser",
                "password": "789",
                "email": "superuser@example.com",
            },
            {
                "username": "goodman",
                "password": "012",
                "email": "superuser@example.com",
            },
        ),
    ),
)
def test_register_duplicated_user(
    api_client, db, django_user_model, user_data, payload
):
    """Tests duplicated user registration."""
    django_user_model.objects.create(**user_data)
    response = api_client.post("/api/auth/register/", payload)

    assert response.status_code == 400


@pytest.mark.parametrize(
    "user_data",
    (
        {
            "username": "superuser",
            "password": "123",
            "email": "superuser@example.com",
        },
    ),
)
def test_login(api_client, db, django_user_model, user_data):
    user = django_user_model.objects.create(**user_data)
    user.set_password(user_data["password"])
    user.save()

    del user_data["email"]
    response = api_client.post("/api/auth/token/login/", user_data)

    assert response.status_code == 200
    result = response.json()
    assert result["access"]
    assert result["refresh"]
