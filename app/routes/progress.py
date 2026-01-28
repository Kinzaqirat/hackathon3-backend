"""
Progress tracking endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.schemas import ProgressResponse
from app.models.models import Progress
from app.routes.auth import get_current_user_payload

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/progress", tags=["progress"])


@router.get("/{student_id}", response_model=list[ProgressResponse])
async def get_student_progress(
    student_id: int,
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get student progress"""
    try:
        # Get current user info
        current_user = get_current_user_payload(request)
        current_user_id = current_user.get("user_id")
        current_role = current_user.get("role")

        # Students can only access their own progress
        # Teachers can access any student's progress
        if current_role == "student" and current_user_id != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Cannot access other students' progress"
            )

        progress = db.query(Progress).filter(
            Progress.student_id == student_id
        ).offset(skip).limit(limit).all()

        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No progress found for student {student_id}"
            )

        return progress
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching student progress: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching progress"
        )


@router.get("/exercise/{exercise_id}", response_model=list[ProgressResponse])
async def get_exercise_progress(
    exercise_id: int,
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get exercise progress statistics"""
    try:
        # Get current user info to ensure they're authenticated
        current_user = get_current_user_payload(request)
        current_user_id = current_user.get("user_id")

        if not current_user_id or current_user_id == 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )

        progress = db.query(Progress).filter(
            Progress.exercise_id == exercise_id
        ).offset(skip).limit(limit).all()

        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No progress found for exercise {exercise_id}"
            )

        return progress
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching exercise progress: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching progress"
        )