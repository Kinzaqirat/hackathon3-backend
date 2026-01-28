"""Quick seed script to populate database"""
import sys
sys.path.insert(0, '.')

from app.core.database import SessionLocal
from app.models.models import Level, Topic, Exercise

def quick_seed():
    db = SessionLocal()
    
    # Create levels
    levels_data = [
        {"name": "Beginner", "description": "Start your Python journey", "order": 1},
        {"name": "Intermediate", "description": "Build complex applications", "order": 2},
        {"name": "Advanced", "description": "Master advanced concepts", "order": 3},
    ]
    
    for ld in levels_data:
        if not db.query(Level).filter(Level.name == ld["name"]).first():
            db.add(Level(**ld))
    db.commit()
    
    # Get levels
    beginner = db.query(Level).filter(Level.name == "Beginner").first()
    intermediate = db.query(Level).filter(Level.name == "Intermediate").first()
    
    # Create topics
    topics_data = [
        {"name": "Introduction to Python", "description": "Learn Python basics", "level_id": beginner.id, "order": 1},
        {"name": "Variables and Data Types", "description": "Master variables and types", "level_id": beginner.id, "order": 2},
        {"name": "Control Flow", "description": "If statements and loops", "level_id": beginner.id, "order": 3},
        {"name": "Functions", "description": "Create reusable code", "level_id": beginner.id, "order": 4},
        {"name": "Data Structures", "description": "Lists, dicts, tuples", "level_id": intermediate.id, "order": 5},
        {"name": "Object-Oriented Programming", "description": "Classes and objects", "level_id": intermediate.id, "order": 6},
    ]
    
    for td in topics_data:
        if not db.query(Topic).filter(Topic.name == td["name"]).first():
            db.add(Topic(**td))
    db.commit()
    
    # Get topics
    intro_topic = db.query(Topic).filter(Topic.name == "Introduction to Python").first()
    vars_topic = db.query(Topic).filter(Topic.name == "Variables and Data Types").first()
    
    # Create exercises
    exercises_data = [
        {
            "title": "Hello, World!",
            "description": "Write a program that prints 'Hello, World!'",
            "difficulty_level": "easy",
            "topic": "Introduction to Python",
            "topic_id": intro_topic.id if intro_topic else None,
            "level_id": beginner.id,
            "starter_code": "# Write your code here\n",
            "expected_output": "Hello, World!",
        },
        {
            "title": "Variables Practice",
            "description": "Create and print variables",
            "difficulty_level": "easy",
            "topic": "Variables and Data Types",
            "topic_id": vars_topic.id if vars_topic else None,
            "level_id": beginner.id,
            "starter_code": "# Create variables\n",
            "expected_output": "Name: John, Age: 25",
        },
        {
            "title": "Simple Calculator",
            "description": "Add two numbers",
            "difficulty_level": "easy",
            "topic": "Variables and Data Types",
            "topic_id": vars_topic.id if vars_topic else None,
            "level_id": beginner.id,
            "starter_code": "# Add two numbers\n",
            "expected_output": "Sum: 15",
        },
    ]
    
    for ed in exercises_data:
        if not db.query(Exercise).filter(Exercise.title == ed["title"]).first():
            db.add(Exercise(**ed))
    db.commit()
    
    print("[SUCCESS] Database seeded successfully!")
    print(f"  - {len(levels_data)} levels")
    print(f"  - {len(topics_data)} topics")
    print(f"  - {len(exercises_data)} exercises")
    
    db.close()

if __name__ == "__main__":
    quick_seed()
