"""
Pytest configuration and fixtures
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.core.database import Base, get_db
from main import app
from app.models import Student, Exercise, Progress


# Use SQLite for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the get_db dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def test_student(db):
    """Create test student"""
    from app.core.security import hash_password
    
    student = Student(
        email="test@example.com",
        name="Test Student",
        password_hash=hash_password("testpass123"),
        grade_level="10",
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@pytest.fixture
def test_exercise(db):
    """Create test exercise"""
    exercise = Exercise(
        title="Test Exercise",
        description="Test Description",
        difficulty_level="beginner",
        topic="python",
        starter_code="print('hello')",
        expected_output="hello",
        test_cases=[{"input": "", "output": "hello"}],
        hints=["Use print()"],
    )
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise


@pytest.fixture
def test_progress(db, test_student, test_exercise):
    """Create test progress"""
    progress = Progress(
        student_id=test_student.id,
        exercise_id=test_exercise.id,
        status="in_progress",
    )
    db.add(progress)
    db.commit()
    db.refresh(progress)
    return progress
