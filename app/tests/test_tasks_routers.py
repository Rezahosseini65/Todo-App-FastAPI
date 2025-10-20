import pytest
from fastapi import status
from app.users.models import User
from app.auths.jwt_auth import generate_access_token
from app.tasks.models import TaskModel


@pytest.mark.usefixtures("setup_database", "override_dependency")
class TestTaskRoutes:
    """Comprehensive tests for the /tasks/ endpoints."""

    @pytest.fixture(scope="class")
    def auth_header(self, db_session):
        """Create a test user and return Authorization header."""
        user = User(username="taskuser")
        user.set_password("Pass1234")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        token = generate_access_token({"user_id": user.id})
        return {"Authorization": f"Bearer {token}"}

    def test_create_task_success(self, anon_client, auth_header, db_session):
        payload = {
            "title": "My first task",
            "description": "test description",
            "is_completed": False
        }

        response = anon_client.post("/tasks/", json=payload, headers=auth_header)
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        assert data["title"] == payload["title"]
        assert data["description"] == payload["description"]
        assert data["is_completed"] is False

        # Verify in DB
        task = db_session.query(TaskModel).filter_by(title="My first task").first()
        assert task is not None

    def test_list_tasks(self, anon_client, auth_header):
        """Should return list of tasks for the user."""
        response = anon_client.get("/tasks/", headers=auth_header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_list_tasks_with_pagination_and_filter(self, anon_client, auth_header):
        """Should handle query params: completed, limit, offset."""
        response = anon_client.get("/tasks/?completed=false&limit=5&offset=0", headers=auth_header)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

    def test_get_task_detail_success(self, anon_client, auth_header, db_session):
        """Retrieve a single existing task."""
        task = db_session.query(TaskModel).first()
        assert task is not None

        response = anon_client.get(f"/tasks/{task.id}/", headers=auth_header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == task.id
        assert data["title"] == task.title

    def test_get_task_detail_not_found(self, anon_client, auth_header):
        response = anon_client.get("/tasks/9999/", headers=auth_header)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.text

    def test_update_task_success(self, anon_client, auth_header, db_session):
        task = db_session.query(TaskModel).first()
        payload = {"title": "Updated title", "is_completed": True}

        response = anon_client.put(f"/tasks/{task.id}/", json=payload, headers=auth_header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated title"
        assert data["is_completed"] is True

    def test_update_task_not_found(self, anon_client, auth_header):
        payload = {"title": "Ghost task", "is_completed": True}
        response = anon_client.put("/tasks/8888/", json=payload, headers=auth_header)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_task_success(self, anon_client, auth_header, db_session):
        """Delete an existing task and verify removal."""
        task = db_session.query(TaskModel).first()
        response = anon_client.delete(f"/tasks/{task.id}/", headers=auth_header)
        assert response.status_code == status.HTTP_200_OK
        assert "removed" in response.text

        # Ensure deleted from DB
        deleted = db_session.query(TaskModel).filter_by(id=task.id).one_or_none()
        assert deleted is None

    def test_delete_task_not_found(self, anon_client, auth_header):
        """Deleting non-existing task should return 404."""
        response = anon_client.delete("/tasks/9999/", headers=auth_header)
        assert response.status_code == status.HTTP_404_NOT_FOUND
