"""
Teacher dashboard endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.schemas import (
    ExerciseCreate, ExerciseUpdate, ExerciseResponse,
    QuizCreate, QuizUpdate, QuizResponse,
    TopicCreate, TopicUpdate, TopicResponse
)
from app.models.models import Teacher, Exercise, Quiz, Topic, Level, QuizSubmission, Progress, QuizQuestion
from app.services import ExerciseService
from app.routes.auth import get_current_teacher_id, get_current_user_payload

router = APIRouter(prefix="/api/teacher", tags=["teacher-dashboard"])
logger = logging.getLogger(__name__)


@router.get("/dashboard", status_code=status.HTTP_200_OK)
async def get_teacher_dashboard(
    current_teacher_id: int = Depends(get_current_teacher_id),
    db: Session = Depends(get_db)
):
    """Get teacher dashboard overview"""
    try:
        # Get counts for dashboard overview - only for this teacher's content
        total_quizzes = db.query(Quiz).filter(Quiz.teacher_id == current_teacher_id).count()
        total_exercises = db.query(Exercise).count()  # This might need to be filtered by teacher too
        total_topics = db.query(Topic).count()  # Topics are shared among teachers
        # Count students who have taken quizzes created by this teacher
        quiz_ids = db.query(Quiz.id).filter(Quiz.teacher_id == current_teacher_id).subquery()
        total_students = db.query(QuizSubmission).filter(
            QuizSubmission.quiz_id.in_(quiz_ids)
        ).distinct(QuizSubmission.student_id).count()

        # Get recent activity for this teacher
        recent_quizzes = db.query(Quiz).filter(Quiz.teacher_id == current_teacher_id).order_by(Quiz.created_at.desc()).limit(5).all()
        recent_exercises = db.query(Exercise).order_by(Exercise.created_at.desc()).limit(5).all()

        return {
            "overview": {
                "total_quizzes": total_quizzes,
                "total_exercises": total_exercises,
                "total_topics": total_topics,
                "total_students": total_students
            },
            "recent_activity": {
                "recent_quizzes": recent_quizzes,
                "recent_exercises": recent_exercises
            }
        }
    except Exception as e:
        logger.error(f"Get teacher dashboard error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get teacher dashboard"
        )


# ============= Exercise Management Endpoints =============

@router.post("/exercises", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED)
async def create_exercise_for_teacher(
    exercise: ExerciseCreate,
    current_teacher_id: int = Depends(get_current_teacher_id),
    db: Session = Depends(get_db)
):
    """Create a new exercise (teacher only)"""
    try:
        db_exercise = ExerciseService.create_exercise(db, exercise, current_teacher_id)
        return db_exercise
    except Exception as e:
        logger.error(f"Create exercise error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create exercise"
        )


@router.put("/exercises/{exercise_id}", response_model=ExerciseResponse)
async def update_exercise_for_teacher(
    exercise_id: int,
    exercise: ExerciseUpdate,
    current_teacher_id: int = Depends(get_current_teacher_id),
    db: Session = Depends(get_db)
):
    """Update an exercise (teacher only)"""
    # Note: ExerciseService.update_exercise may need to be updated to check ownership
    # For now, we'll just verify the teacher is authenticated
    db_exercise = ExerciseService.update_exercise(db, exercise_id, exercise)
    if not db_exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )
    return db_exercise


@router.delete("/exercises/{exercise_id}")
async def delete_exercise_for_teacher(
    exercise_id: int,
    current_teacher_id: int = Depends(get_current_teacher_id),
    db: Session = Depends(get_db)
):
    """Delete an exercise (teacher only)"""
    # Note: ExerciseService.delete_exercise may need to be updated to check ownership
    # For now, we'll just verify the teacher is authenticated
    if not ExerciseService.delete_exercise(db, exercise_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )
    return {"message": "Exercise deleted"}


# ============= Quiz Management Endpoints =============

@router.post("/quizzes", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def create_quiz_for_teacher(
    quiz: QuizCreate,
    current_teacher_id: int = Depends(get_current_teacher_id),
    db: Session = Depends(get_db)
):
    """Create a new quiz (teacher only)"""
    try:
        # Create quiz with the authenticated teacher's ID
        db_quiz = Quiz(
            title=quiz.title,
            description=quiz.description,
            topic_id=quiz.topic_id,
            level_id=quiz.level_id,
            teacher_id=current_teacher_id,  # Use the authenticated teacher's ID
            passing_score=quiz.passing_score,
            time_limit_minutes=quiz.time_limit_minutes,
            shuffle_questions=quiz.shuffle_questions
        )
        db.add(db_quiz)
        db.flush()

        # Create questions if provided
        if quiz.questions:
            for q in quiz.questions:
                db_question = QuizQuestion(
                    quiz_id=db_quiz.id,
                    **q.dict()
                )
                db.add(db_question)

        db.commit()
        db.refresh(db_quiz)
        return db_quiz
    except Exception as e:
        db.rollback()
        logger.error(f"Create quiz error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create quiz"
        )


@router.put("/quizzes/{quiz_id}", response_model=QuizResponse)
async def update_quiz_for_teacher(
    quiz_id: int,
    quiz_update: QuizUpdate,
    current_teacher_id: int = Depends(get_current_teacher_id),
    db: Session = Depends(get_db)
):
    """Update a quiz (teacher only)"""
    try:
        db_quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.teacher_id == current_teacher_id).first()
        if not db_quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found or does not belong to current teacher"
            )

        update_data = quiz_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_quiz, key, value)

        db.commit()
        db.refresh(db_quiz)
        return db_quiz
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Update quiz error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update quiz"
        )


@router.delete("/quizzes/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quiz_for_teacher(
    quiz_id: int,
    current_teacher_id: int = Depends(get_current_teacher_id),
    db: Session = Depends(get_db)
):
    """Delete a quiz (teacher only)"""
    try:
        db_quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.teacher_id == current_teacher_id).first()
        if not db_quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found or does not belong to current teacher"
            )

        db.delete(db_quiz)
        db.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Delete quiz error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete quiz"
        )


# ============= Topic Management Endpoints =============

@router.post("/topics", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
async def create_topic_for_teacher(
    topic: TopicCreate,
    current_teacher_id: int = Depends(get_current_teacher_id),
    db: Session = Depends(get_db)
):
    """Create a new topic (teacher only)"""
    try:
        db_topic = Topic(
            name=topic.name,
            description=topic.description,
            level_id=topic.level_id,
            order=topic.order,
            learning_objectives=topic.learning_objectives,
            resources=topic.resources
        )
        db.add(db_topic)
        db.commit()
        db.refresh(db_topic)
        return db_topic
    except Exception as e:
        db.rollback()
        logger.error(f"Create topic error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create topic"
        )


@router.put("/topics/{topic_id}", response_model=TopicResponse)
async def update_topic_for_teacher(
    topic_id: int,
    topic: TopicUpdate,
    current_teacher_id: int = Depends(get_current_teacher_id),
    db: Session = Depends(get_db)
):
    """Update a topic (teacher only)"""
    try:
        db_topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not db_topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found"
            )

        update_data = topic.dict(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(db_topic, key) and value is not None:
                setattr(db_topic, key, value)

        db.commit()
        db.refresh(db_topic)
        return db_topic
    except Exception as e:
        db.rollback()
        logger.error(f"Update topic error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update topic"
        )


@router.delete("/topics/{topic_id}")
async def delete_topic_for_teacher(
    topic_id: int,
    current_teacher_id: int = Depends(get_current_teacher_id),
    db: Session = Depends(get_db)
):
    """Delete a topic (teacher only)"""
    try:
        db_topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not db_topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found"
            )

        # Check if topic has associated exercises or quizzes
        exercises_count = db.query(Exercise).filter(Exercise.topic_id == topic_id).count()
        quizzes_count = db.query(Quiz).filter(Quiz.topic_id == topic_id).count()

        if exercises_count > 0 or quizzes_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete topic with associated exercises or quizzes"
            )

        db.delete(db_topic)
        db.commit()
        return {"message": "Topic deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Delete topic error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete topic"
        )


# ============= Review and Analytics Endpoints =============

@router.get("/reviews/submissions", response_model=dict)
async def get_pending_reviews(
    current_teacher_id: int = Depends(get_current_teacher_id),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get pending submissions for review"""
    try:
        from app.models.models import ExerciseSubmission

        # Get submissions that need review (e.g., those with status 'submitted' but not yet graded)
        # Note: This assumes there's a way to link submissions to teachers
        # For now, we'll just verify the teacher is authenticated
        pending_submissions = db.query(ExerciseSubmission).filter(
            ExerciseSubmission.status == "submitted"
        ).offset(skip).limit(limit).all()

        # Also get recently submitted exercises
        recent_submissions = db.query(ExerciseSubmission).order_by(
            ExerciseSubmission.submitted_at.desc()
        ).limit(10).all()

        return {
            "pending_submissions": pending_submissions,
            "recent_submissions": recent_submissions,
            "total_pending": len(pending_submissions)
        }
    except Exception as e:
        logger.error(f"Get pending reviews error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get pending reviews"
        )


@router.get("/reviews/progress", response_model=dict)
async def get_class_progress(
    current_teacher_id: int = Depends(get_current_teacher_id),
    topic_id: int = Query(None),
    level_id: int = Query(None),
    db: Session = Depends(get_db)
):
    """Get class progress analytics"""
    try:
        # Get all students
        from app.models.models import Student

        students = db.query(Student).all()

        # Get progress data
        progress_query = db.query(Progress)
        if topic_id:
            progress_query = progress_query.join(Exercise).filter(Exercise.topic_id == topic_id)
        if level_id:
            progress_query = progress_query.join(Exercise).filter(Exercise.level_id == level_id)

        progress_data = progress_query.all()

        # Calculate overall class statistics
        total_students = len(students)
        total_progress_records = len(progress_data)

        completed_progress = [p for p in progress_data if p.status in ["completed", "mastered"]]
        in_progress = [p for p in progress_data if p.status == "in_progress"]

        # Calculate completion rates
        completion_rate = (len(completed_progress) / total_progress_records * 100) if total_progress_records > 0 else 0

        return {
            "class_overview": {
                "total_students": total_students,
                "total_exercises_tracked": total_progress_records,
                "completed_exercises": len(completed_progress),
                "in_progress_exercises": len(in_progress),
                "completion_rate": completion_rate
            },
            "detailed_progress": [
                {
                    "student_id": p.student_id,
                    "exercise_id": p.exercise_id,
                    "status": p.status,
                    "best_score": p.best_score,
                    "attempts": p.attempts
                }
                for p in progress_data[:20]  # Limit to first 20 for performance
            ]
        }
    except Exception as e:
        logger.error(f"Get class progress error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get class progress"
        )


# ============= Teacher Settings Endpoints =============

@router.get("/settings", response_model=dict)
async def get_teacher_settings(
    current_teacher_id: int = Depends(get_current_teacher_id),
    db: Session = Depends(get_db)
):
    """Get teacher settings"""
    try:
        # For now, return a basic settings structure
        # In a real implementation, this would fetch from a settings table
        return {
            "notifications_enabled": True,
            "email_notifications": True,
            "auto_grade_exercises": True,
            "allow_student_messages": True,
            "dashboard_preferences": {
                "default_view": "overview",
                "show_completed": True,
                "show_pending": True
            }
        }
    except Exception as e:
        logger.error(f"Get teacher settings error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get teacher settings"
        )


@router.put("/settings", response_model=dict)
async def update_teacher_settings(
    settings: dict,
    current_teacher_id: int = Depends(get_current_teacher_id),
    db: Session = Depends(get_db)
):
    """Update teacher settings"""
    try:
        # For now, just validate and return the settings
        # In a real implementation, this would save to a settings table
        required_fields = ["notifications_enabled", "email_notifications", "auto_grade_exercises"]

        for field in required_fields:
            if field not in settings:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )

        return {
            "message": "Settings updated successfully",
            "updated_settings": settings
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update teacher settings error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update teacher settings"
        )


