"""
Exercise endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.schemas import ExerciseResponse, ExerciseCreate, ExerciseUpdate
from app.services import ExerciseService
from app.routes.auth import get_current_user_payload, get_current_teacher_id

router = APIRouter(prefix="/api/exercises", tags=["exercises"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED)
async def create_exercise(
    exercise: ExerciseCreate,
    current_teacher_id: int = Depends(get_current_teacher_id),
    db: Session = Depends(get_db)
):
    """Create a new exercise (Teachers only)"""
    try:
        db_exercise = ExerciseService.create_exercise(db, exercise, current_teacher_id)
        return db_exercise
    except Exception as e:
        logger.error(f"Create exercise error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create exercise"
        )


@router.get("/{exercise_id}", response_model=ExerciseResponse)
async def get_exercise(
    request: Request,
    exercise_id: int,
    db: Session = Depends(get_db)
):
    """Get exercise by ID"""
    try:
        # Check if user is authenticated
        current_user = get_current_user_payload(request)
        current_user_id = current_user.get("user_id")

        if not current_user_id or current_user_id == 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )

        exercise = ExerciseService.get_exercise(db, exercise_id)
        if not exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exercise not found"
            )

        # Convert to response object to avoid relationship serialization issues
        exercise_resp = ExerciseResponse(
            id=exercise.id,
            title=exercise.title,
            description=exercise.description,
            difficulty_level=exercise.difficulty_level,
            topic=exercise.topic,
            starter_code=exercise.starter_code,
            expected_output=exercise.expected_output,
            test_cases=exercise.test_cases,
            hints=exercise.hints,
            created_at=exercise.created_at,
            updated_at=exercise.updated_at
        )
        return exercise_resp
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get exercise error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get exercise"
        )


@router.get("/", response_model=list[ExerciseResponse])
async def list_exercises(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    topic: str = Query(None),
    difficulty: str = Query(None),
    db: Session = Depends(get_db)
):
    """List exercises with optional filters"""
    try:
        # Check if user is authenticated
        current_user = get_current_user_payload(request)
        current_user_id = current_user.get("user_id")

        if not current_user_id or current_user_id == 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )

        if topic:
            exercises = ExerciseService.get_exercises_by_topic(db, topic, skip, limit)
        elif difficulty:
            exercises = ExerciseService.get_exercises_by_difficulty(db, difficulty, skip, limit)
        else:
            exercises = ExerciseService.get_all_exercises(db, skip, limit)

        # Convert to response objects to avoid relationship serialization issues
        exercise_responses = []
        for exercise in exercises:
            exercise_resp = ExerciseResponse(
                id=exercise.id,
                title=exercise.title,
                description=exercise.description,
                difficulty_level=exercise.difficulty_level,
                topic=exercise.topic,
                starter_code=exercise.starter_code,
                expected_output=exercise.expected_output,
                test_cases=exercise.test_cases,
                hints=exercise.hints,
                created_at=exercise.created_at,
                updated_at=exercise.updated_at
            )
            exercise_responses.append(exercise_resp)

        return exercise_responses
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List exercises error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list exercises"
        )


@router.put("/{exercise_id}", response_model=ExerciseResponse)
async def update_exercise(
    exercise_id: int,
    exercise: ExerciseUpdate,
    current_teacher_id: int = Depends(get_current_teacher_id),
    db: Session = Depends(get_db)
):
    """Update an exercise (Teachers only)"""
    db_exercise = ExerciseService.update_exercise(db, exercise_id, exercise)
    if not db_exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )
    return db_exercise


@router.delete("/{exercise_id}")
async def delete_exercise(
    exercise_id: int,
    current_teacher_id: int = Depends(get_current_teacher_id),
    db: Session = Depends(get_db)
):
    """Delete an exercise (Teachers only)"""
    if not ExerciseService.delete_exercise(db, exercise_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )
    return {"message": "Exercise deleted"}
