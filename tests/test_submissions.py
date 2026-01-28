"""
Submission tests
"""

import pytest
from fastapi import status


def test_create_submission(client, test_student, test_exercise):
    """Test code submission"""
    response = client.post(
        "/api/submissions/",
        json={
            "student_id": test_student.id,
            "exercise_id": test_exercise.id,
            "code": "print('hello')",
            "language": "python",
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["code"] == "print('hello')"
    assert data["status"] == "submitted"


def test_get_submission(client, test_student, test_exercise):
    """Test get submission"""
    # Create submission first
    create_response = client.post(
        "/api/submissions/",
        json={
            "student_id": test_student.id,
            "exercise_id": test_exercise.id,
            "code": "code",
            "language": "python",
        }
    )
    submission_id = create_response.json()["id"]
    
    # Get submission
    response = client.get(f"/api/submissions/{submission_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == submission_id


def test_get_student_submissions(client, test_student, test_exercise):
    """Test get student submissions"""
    response = client.get(f"/api/submissions/student/{test_student.id}")
    assert response.status_code == status.HTTP_200_OK


def test_get_exercise_submissions(client, test_exercise):
    """Test get exercise submissions"""
    response = client.get(f"/api/submissions/exercise/{test_exercise.id}")
    assert response.status_code == status.HTTP_200_OK
