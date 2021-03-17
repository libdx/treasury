def test_get_all_users(api_client, db):
    response = api_client.get("/api/users/")
    assert response.status_code == 200


def test_get_user(api_client, db, django_user_model):
    django_user_model.objects.create(username="superuser", password="123")

    response = api_client.get("/api/users/")

    assert response.status_code == 200
    result = response.json()
    assert len(result) == 1
    assert "password" not in result
