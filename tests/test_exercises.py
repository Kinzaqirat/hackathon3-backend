"""
Exercise tests
"""

import pytest
from fastapi import status


def test_create_exercise(client):
    """Test exercise creation"""
    response = client.post(
        "/api/exercises/",
        json={
            "title": "Python Basics",
            "description": "Learn Python",
            "difficulty_level": "beginner",
            "topic": "python",
            "starter_code": "# Code",
            "expected_output": "output",
            "test_cases": [{"input": "", "output": "output"}],
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "Python Basics"


def test_get_exercise(client, test_exercise):
    """Test get exercise"""
    response = client.get(f"/api/exercises/{test_exercise.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_exercise.id
    assert data["title"] == test_exercise.title


def test_get_nonexistent_exercise(client):
    """Test get non-existent exercise"""
    response = client.get("/api/exercises/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_exercises(client, test_exercise):
    """Test list exercises"""
    response = client.get("/api/exercises/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1


def test_update_exercise(client, test_exercise):
    """Test update exercise"""
    response = client.put(
        f"/api/exercises/{test_exercise.id}",
        json={"title": "Updated Title"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Updated Title"


def test_delete_exercise(client, test_exercise):
    """Test delete exercise"""
    response = client.delete(f"/api/exercises/{test_exercise.id}")
    assert response.status_code == status.HTTP_200_OK
    
    # Verify it's deleted
    response = client.get(f"/api/exercises/{test_exercise.id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
