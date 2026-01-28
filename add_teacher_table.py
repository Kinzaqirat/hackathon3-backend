"""
Migration script to add Teacher table and update Quiz table
"""

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.database import Base
from app.models.models import Teacher, Quiz  # Import the models

# Create database engine
engine = create_engine(settings.database_url)

def run_migration():
    print("Creating Teacher table...")

    # Create all tables (this will only create tables that don't exist)
    Base.metadata.create_all(bind=engine)

    # Add teacher_id column to quizzes table if it doesn't exist (for SQLite)
    with engine.connect() as conn:
        # Get table info for quizzes table in SQLite
        result = conn.execute(text("PRAGMA table_info(quizzes)"))
        columns = [row[1] for row in result.fetchall()]  # Column names are in the second position

        if 'teacher_id' not in columns:
            print("Adding teacher_id column to quizzes table...")
            conn.execute(text("ALTER TABLE quizzes ADD COLUMN teacher_id INTEGER"))
            conn.commit()
            print("Column added successfully!")
        else:
            print("teacher_id column already exists.")

    print("Migration completed successfully!")

if __name__ == "__main__":
    run_migration()