import pytest
from django.contrib.auth import get_user_model


def test_health(client):
    response = client.get("/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.django_db
def test_obtain_jwt_token(api_client):
    get_user_model().objects.create_user(username="alice", password="s3cret-pass!")

    response = api_client.post(
        "/api/auth/token/", {"username": "alice", "password": "s3cret-pass!"}, format="json"
    )

    assert response.status_code == 200
    assert {"access", "refresh"} <= response.json().keys()
