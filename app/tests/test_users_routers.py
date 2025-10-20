import pytest
from fastapi import status
from app.users.models import User


@pytest.mark.usefixtures("setup_database", "override_dependency")
class TestUserRoutes:

    def test_register_success(self, anon_client, db_session):
        payload = {
            "username": "testuser",
            "password": "StrongPass123",
            "confirm_password": "StrongPass123"
        }

        response = anon_client.post("/users/register/", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

        # Verify in DB
        user_in_db = db_session.query(User).filter_by(username="testuser").first()
        assert user_in_db is not None
        assert user_in_db.username == "testuser"


    def test_register_duplicate_username(self, anon_client):
        payload = {
            "username": "testuser",
            "password": "AnotherPass123",
            "confirm_password": "AnotherPass123"
        }

        response = anon_client.post("/users/register/", json=payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "username alredy exists" in response.text


    def test_login_success(self, anon_client):
        payload = {
            "username": "testuser",
            "password": "StrongPass123"
        }

        response = anon_client.post("/users/login/", json=payload)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"


    def test_login_wrong_password(self, anon_client):
            payload = {
                "username": "testuser",
                "password": "WrongPass!"
            }

            response = anon_client.post("/users/login/", json=payload)

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert "Invalid username or password" in data["detail"]["message"]

    def test_login_nonexistent_user(self, anon_client):
        payload = {
            "username": "ghostuser",
            "password": "SomePass123"
        }

        response = anon_client.post("/users/login/", json=payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "Invalid username or password" in data["detail"]["message"]

    def test_register_username_case_insensitive(self, anon_client, db_session):
        payload = {
            "username": "TestUser",
            "password": "Pass321!",
            "confirm_password": "Pass321!"
        }

        response = anon_client.post("/users/register/", json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "username alredy exists" in response.text

    def test_register_invalid_payload(self, anon_client):
        # Missing password
        payload = {"username": "newuser"}
        response = anon_client.post("/users/register/", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        # Missing username
        payload = {"password": "NoUserPass"}
        response = anon_client.post("/users/register/", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT