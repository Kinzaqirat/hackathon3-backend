"""
Progress tracking and analytics endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging

from app.core.database import get_db
from app.schemas import ProgressResponse, StudentStats, ExerciseStats
from app.models.models import Exercise, Progress
from app.routes.auth import get_current_teacher_id

router = APIRouter(prefix="/api/analytics", tags=["analytics"])
logger = logging.getLogger(__name__)


@router.get("/student/{student_id}/progress", response_model=list[ProgressResponse])
async def get_student_progress(
    student_id: int,
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get student progress on all exercises"""
    try:
        from app.routes.auth import get_current_user_payload

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
            return []

        return progress
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching student progress: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get student progress"
        )


@router.get("/student/{student_id}/stats", response_model=StudentStats)
async def get_student_stats(
    student_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get student statistics"""
    try:
        from app.routes.auth import get_current_user_payload

        # Get current user info
        current_user = get_current_user_payload(request)
        current_user_id = current_user.get("user_id")
        current_role = current_user.get("role")

        # Students can only access their own stats
        # Teachers can access any student's stats
        if current_role == "student" and current_user_id != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Cannot access other students' stats"
            )

        total_exercises = db.query(Exercise).count()

        completed_exercises = db.query(Progress).filter(
            Progress.student_id == student_id,
            Progress.status.in_(["completed", "mastered"])
        ).count()

        score_data = db.query(Progress).filter(
            Progress.student_id == student_id,
            Progress.best_score != None
        ).all()

        average_score = sum(p.best_score for p in score_data) / len(score_data) if score_data else 0

        return StudentStats(
            student_id=student_id,
            total_exercises=total_exercises,
            completed_exercises=completed_exercises,
            average_score=average_score,
            total_time_spent_minutes=0,
            last_activity=None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get student stats error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get student statistics"
        )


@router.get("/exercise/{exercise_id}/stats", response_model=ExerciseStats)
async def get_exercise_stats(
    exercise_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get exercise statistics"""
    try:
        from app.routes.auth import get_current_user_payload

        # Get current user info to ensure they're authenticated
        current_user = get_current_user_payload(request)
        current_user_id = current_user.get("user_id")

        if not current_user_id or current_user_id == 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )

        total_attempts = db.query(Progress).filter(
            Progress.exercise_id == exercise_id
        ).count()

        successful_attempts = db.query(Progress).filter(
            Progress.exercise_id == exercise_id,
            Progress.status.in_(["completed", "mastered"])
        ).count()

        score_data = db.query(Progress).filter(
            Progress.exercise_id == exercise_id,
            Progress.best_score != None
        ).all()

        average_score = sum(p.best_score for p in score_data) / len(score_data) if score_data else 0

        return ExerciseStats(
            exercise_id=exercise_id,
            total_attempts=total_attempts,
            successful_attempts=successful_attempts,
            average_score=average_score,
            average_time_minutes=0.0
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get exercise stats error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get exercise statistics"
        )


@router.get("/students")
async def get_all_students_analytics(
    current_teacher_id: int = Depends(get_current_teacher_id),
    db: Session = Depends(get_db)
):
    """Get analytics for all students (Teachers only)"""
    try:
        # Get all students with their basic info and some stats
        from app.models.models import Student  # Import here to avoid circular import

        students = db.query(Student).all()

        result = []
        for student in students:
            # Get student progress stats
            total_exercises = db.query(Progress).filter(
                Progress.student_id == student.id
            ).count()

            from app.models.models import QuizSubmission
            quizzes_passed = db.query(QuizSubmission).filter(
                QuizSubmission.student_id == student.id,
                QuizSubmission.passed == True
            ).count()

            average_score = sum(p.best_score for p in score_data) / len(score_data) if score_data else 0

            # Format last active for display
            last_active_str = "Never"
            if student.updated_at:
                # Simple relative time approximation for display
                from datetime import datetime
                diff = datetime.utcnow() - student.updated_at
                if diff.days > 0:
                    last_active_str = f"{diff.days} days ago"
                elif diff.seconds > 3600:
                    last_active_str = f"{diff.seconds // 3600} hours ago"
                elif diff.seconds > 60:
                    last_active_str = f"{diff.seconds // 60} mins ago"
                else:
                    last_active_str = "Just now"

            result.append({
                "id": student.id,
                "name": student.name,
                "email": student.email,
                "grade_level": student.grade_level,
                "exercises_completed": completed_exercises,
                "quizzes_passed": quizzes_passed,
                "last_active": last_active_str,
                "total_exercises": total_exercises,
                "average_score": average_score
            })

        return result
    except Exception as e:
        logger.error(f"Get all students analytics error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get students analytics"
        )


@router.get("/leaderboard")
async def get_leaderboard(
    request: Request,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get top students leaderboard"""
    try:
        from app.routes.auth import get_current_user_payload

        # Get current user info to ensure they're authenticated
        current_user = get_current_user_payload(request)
        current_user_id = current_user.get("user_id")

        if not current_user_id or current_user_id == 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )

        top_students = db.query(
            Progress.student_id,
            func.count(Progress.id).label("exercises_completed"),
            func.avg(Progress.best_score).label("average_score")
        ).filter(
            Progress.status.in_(["completed", "mastered"])
        ).group_by(
            Progress.student_id
        ).order_by(
            func.count(Progress.id).desc(),
            func.avg(Progress.best_score).desc()
        ).limit(limit).all()

        return {
            "leaderboard": [
                {
                    "rank": idx + 1,
                    "student_id": student[0],
                    "exercises_completed": student[1],
                    "average_score": float(student[2]) if student[2] else 0
                }
                for idx, student in enumerate(top_students)
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get leaderboard error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get leaderboard"
        )
