"""
Authentication tests
"""

import pytest
from fastapi import status


def test_register_student(client):
    """Test student registration"""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "newstudent@example.com",
            "name": "New Student",
            "password": "securepass123",
            "grade_level": "10",
        }
    )
    assert response.status_code == status.HTTP_201_CREATED or response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "newstudent@example.com"
    assert data["name"] == "New Student"


def test_register_duplicate_email(client, test_student):
    """Test registration with duplicate email"""
    response = client.post(
        "/api/auth/register",
        json={
            "email": test_student.email,
            "name": "Another Student",
            "password": "pass123",
            "grade_level": "10",
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_login_success(client, test_student):
    """Test successful login"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": test_student.email,
            "password": "testpass123",
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_invalid_password(client, test_student):
    """Test login with invalid password"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": test_student.email,
            "password": "wrongpass",
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_nonexistent_user(client):
    """Test login for non-existent user"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "pass123",
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
