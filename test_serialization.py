# Test script to isolate the serialization issue
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import Level as LevelModel
from app.schemas.schemas import LevelResponse

# Create a simple test
def test_serialization():
    # Create a mock level object-like dictionary
    mock_level = {
        'id': 1,
        'name': 'Test Level',
        'description': 'A test level',
        'order': 1,
        'created_at': datetime.now()
    }
    
    # Try to create a response object
    try:
        response = LevelResponse(**mock_level)
        print("Success: Created LevelResponse object")
        print(f"Response: {response}")
        print(f"Response dict: {response.dict()}")
    except Exception as e:
        print(f"Error creating LevelResponse: {e}")

if __name__ == "__main__":
    test_serialization()