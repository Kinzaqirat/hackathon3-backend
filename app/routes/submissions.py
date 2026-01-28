"""
Exercise submission endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.schemas import SubmissionResponse, SubmissionCreate, CodeExecutionResultResponse
from app.services import SubmissionService, ExerciseService, ProgressService
from app.services.kafka_service import KafkaService
from app.routes.auth import get_current_user_payload, get_current_teacher_id

router = APIRouter(prefix="/api/submissions", tags=["submissions"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def create_submission(
    submission: SubmissionCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Submit code for an exercise"""
    try:
        # Get current user info
        current_user = get_current_user_payload(request)
        current_user_id = current_user.get("user_id")
        current_role = current_user.get("role")

        # Only students can create submissions
        if current_role != "student":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only students can submit code"
            )

        # Students can only submit for themselves
        if submission.student_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot submit code for another student"
            )

        # Verify exercise exists
        exercise = ExerciseService.get_exercise(db, submission.exercise_id)
        if not exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exercise not found"
            )

        # Create submission
        db_submission = SubmissionService.create_submission(
            db,
            submission.student_id,
            submission.exercise_id,
            submission.code,
            submission.language
        )

        # Publish event to Kafka
        await KafkaService.publish_submission_event(
            submission.student_id,
            submission.exercise_id,
            db_submission.id,
            "submitted"
        )

        return db_submission
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create submission error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create submission"
        )


@router.get("/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get submission by ID"""
    try:
        # Get current user info
        current_user = get_current_user_payload(request)
        current_user_id = current_user.get("user_id")
        current_role = current_user.get("role")

        submission = SubmissionService.get_submission(db, submission_id)
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )

        # Students can only access their own submissions
        # Teachers can access any submission
        if current_role == "student" and submission.student_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Cannot access other students' submissions"
            )

        return submission
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get submission error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get submission"
        )


@router.get("/student/{student_id}", response_model=list[SubmissionResponse])
async def get_student_submissions(
    student_id: int,
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all submissions for a student"""
    try:
        # Get current user info
        current_user = get_current_user_payload(request)
        current_user_id = current_user.get("user_id")
        current_role = current_user.get("role")

        # Students can only access their own submissions
        # Teachers can access any student's submissions
        if current_role == "student" and current_user_id != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Cannot access other students' submissions"
            )

        return SubmissionService.get_student_submissions(db, student_id, skip, limit)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get student submissions error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get student submissions"
        )


@router.get("/exercise/{exercise_id}", response_model=list[SubmissionResponse])
async def get_exercise_submissions(
    exercise_id: int,
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all submissions for an exercise"""
    try:
        # Get current user info
        current_user = get_current_user_payload(request)
        current_user_id = current_user.get("user_id")
        current_role = current_user.get("role")

        # Only teachers can access all submissions for an exercise
        if current_role != "teacher":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Only teachers can access all submissions for an exercise"
            )

        return SubmissionService.get_exercise_submissions(db, exercise_id, skip, limit)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get exercise submissions error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get exercise submissions"
        )


@router.put("/{submission_id}/evaluate")
async def evaluate_submission(
    submission_id: int,
    status: str,
    request: Request,
    score: int = Query(None, ge=0, le=100),
    feedback: str = Query(None),
    db: Session = Depends(get_db)
):
    """Evaluate a submission (Teachers only)"""
    try:
        current_teacher_id = get_current_teacher_id(request)

        submission = SubmissionService.get_submission(db, submission_id)
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )

        # Update submission
        updated_submission = SubmissionService.update_submission_status(
            db,
            submission_id,
            status,
            score,
            feedback
        )

        # Update progress
        ProgressService.update_progress(
            db,
            submission.student_id,
            submission.exercise_id,
            status,
            score
        )

        # Publish events to Kafka
        await KafkaService.publish_submission_event(
            submission.student_id,
            submission.exercise_id,
            submission_id,
            status
        )

        await KafkaService.publish_progress_event(
            submission.student_id,
            submission.exercise_id,
            status,
            score
        )

        return {"message": "Submission evaluated", "submission": updated_submission}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Evaluate submission error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to evaluate submission"
        )
