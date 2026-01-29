"""
FastAPI application for LearnFlow platform
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_db
from app.routes import (
    auth_router,
    exercises_router,
    submissions_router,
    progress_router,
    chat_router,
    analytics_router,
    topics_router,
    quizzes_router,
)

from app.routes.teacher_dashboard import router as teacher_dashboard_router
from app.services.kafka_service import KafkaService
from app.services.enhanced_kafka_service import EnhancedKafkaService
from app.services.dapr_service import DaprService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    logger.info("Starting LearnFlow API...")
    init_db()
    logger.info("Database initialized")

    # Initialize Dapr if available
    try:
        # Test Dapr connectivity
        with DaprService.get_client():
            logger.info("Dapr initialized successfully")
    except Exception as e:
        logger.warning(f"Dapr not available: {str(e)}. Continuing without Dapr.")

    yield

    # Shutdown
    logger.info("Shutting down LearnFlow API...")
    await KafkaService.close_producer()
    await EnhancedKafkaService.close_producer()  # Close enhanced service producer too
    logger.info("Kafka producers closed")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="LearnFlow Learning Platform API",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex="https?://.*\.vercel\.app|https?://localhost.*",  # Allow Vercel and localhost
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to LearnFlow API",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "app": settings.app_name}


# Seed database endpoint
@app.post("/seed")
async def seed_database():
    """Seed database with Python learning content"""
    from app.core.database import SessionLocal, Base, engine
    from app.models.models import Level, Topic, Exercise
    from sqlalchemy import text, inspect
    
    db = None
    try:
        # Ensure tables exist
        Base.metadata.create_all(bind=engine)
        
        # Check if exercises table has topic_id and level_id columns
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('exercises')]
        
        # Add missing columns if needed
        with engine.connect() as conn:
            if 'topic_id' not in columns:
                conn.execute(text('ALTER TABLE exercises ADD COLUMN topic_id INTEGER'))
                conn.commit()
                logger.info("Added topic_id column to exercises table")
            
            if 'level_id' not in columns:
                conn.execute(text('ALTER TABLE exercises ADD COLUMN level_id INTEGER'))
                conn.commit()
                logger.info("Added level_id column to exercises table")
        
        db = SessionLocal()
        
        # Create default student if doesn't exist
        from app.models.models import Student
        from passlib.context import CryptContext
        
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        existing_student = db.query(Student).filter(Student.id == 1).first()
        if not existing_student:
            default_student = Student(
                email="demo@learnflow.com",
                name="Demo Student",
                password_hash=pwd_context.hash("demo123"),
                grade_level="Beginner",
                is_active=True
            )
            db.add(default_student)
            db.commit()
            logger.info("Created default demo student")
        
        # Create levels
        levels_data = [
            {"name": "Beginner", "description": "Start your Python journey", "order": 1},
            {"name": "Intermediate", "description": "Build complex applications", "order": 2},
            {"name": "Advanced", "description": "Master advanced concepts", "order": 3},
        ]
        
        levels_created = 0
        for ld in levels_data:
            existing = db.query(Level).filter(Level.name == ld["name"]).first()
            if not existing:
                db.add(Level(**ld))
                levels_created += 1
        db.commit()
        
        # Get levels
        beginner = db.query(Level).filter(Level.name == "Beginner").first()
        intermediate = db.query(Level).filter(Level.name == "Intermediate").first()
        
        if not beginner or not intermediate:
            raise Exception("Failed to create or retrieve levels")
        
        # Create topics
        topics_data = [
            {"name": "Introduction to Python", "description": "Learn Python basics", "level_id": beginner.id, "order": 1},
            {"name": "Variables and Data Types", "description": "Master variables and types", "level_id": beginner.id, "order": 2},
            {"name": "Control Flow", "description": "If statements and loops", "level_id": beginner.id, "order": 3},
            {"name": "Functions", "description": "Create reusable code", "level_id": beginner.id, "order": 4},
            {"name": "Data Structures", "description": "Lists, dicts, tuples", "level_id": intermediate.id, "order": 5},
            {"name": "Object-Oriented Programming", "description": "Classes and objects", "level_id": intermediate.id, "order": 6},
        ]
        
        topics_created = 0
        for td in topics_data:
            existing = db.query(Topic).filter(Topic.name == td["name"]).first()
            if not existing:
                db.add(Topic(**td))
                topics_created += 1
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
        
        exercises_created = 0
        for ed in exercises_data:
            existing = db.query(Exercise).filter(Exercise.title == ed["title"]).first()
            if not existing:
                db.add(Exercise(**ed))
                exercises_created += 1
        db.commit()
        
        return {
            "status": "success",
            "message": f"Database seeded successfully! Created {levels_created} levels, {topics_created} topics, {exercises_created} exercises"
        }
    except Exception as e:
        if db:
            db.rollback()
        logger.error(f"Seed error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Seed failed: {str(e)}"}
        )
    finally:
        if db:
            db.close()


# Include routers
app.include_router(auth_router)
app.include_router(exercises_router)
app.include_router(submissions_router)
app.include_router(progress_router)
app.include_router(chat_router)
app.include_router(analytics_router)
app.include_router(topics_router)
app.include_router(quizzes_router)
app.include_router(teacher_dashboard_router)


# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug
    )
