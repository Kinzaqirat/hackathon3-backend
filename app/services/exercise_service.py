"""
Exercise service
"""

from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.models import Exercise, ExerciseSubmission, Progress, Student
from app.schemas import ExerciseCreate, ExerciseUpdate

logger = logging.getLogger(__name__)


class ExerciseService:
    """Exercise management service"""
    
    @staticmethod
    def create_exercise(db: Session, exercise_data: ExerciseCreate, teacher_id: int = None) -> Exercise:
        """Create a new exercise"""
        db_exercise = Exercise(
            title=exercise_data.title,
            description=exercise_data.description,
            difficulty_level=exercise_data.difficulty_level,
            topic=exercise_data.topic,
            starter_code=exercise_data.starter_code,
            expected_output=exercise_data.expected_output,
            test_cases=exercise_data.test_cases,
            hints=exercise_data.hints,
            solution_code=exercise_data.solution_code,
        )
        # Add teacher_id if provided and the model supports it
        if teacher_id is not None:
            if hasattr(Exercise, 'teacher_id'):
                db_exercise.teacher_id = teacher_id

        db.add(db_exercise)
        db.commit()
        db.refresh(db_exercise)
        logger.info(f"Exercise created: {db_exercise.id} - {db_exercise.title}")
        return db_exercise
    
    @staticmethod
    def get_exercise(db: Session, exercise_id: int) -> Optional[Exercise]:
        """Get exercise by ID"""
        return db.query(Exercise).filter(Exercise.id == exercise_id).first()
    
    @staticmethod
    def get_all_exercises(db: Session, skip: int = 0, limit: int = 100) -> List[Exercise]:
        """Get all exercises with pagination"""
        return db.query(Exercise).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_exercises_by_topic(db: Session, topic: str, skip: int = 0, limit: int = 100) -> List[Exercise]:
        """Get exercises by topic"""
        return db.query(Exercise).filter(
            Exercise.topic == topic
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_exercises_by_difficulty(db: Session, difficulty: str, skip: int = 0, limit: int = 100) -> List[Exercise]:
        """Get exercises by difficulty level"""
        return db.query(Exercise).filter(
            Exercise.difficulty_level == difficulty
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_exercise(db: Session, exercise_id: int, exercise_data: ExerciseUpdate) -> Optional[Exercise]:
        """Update an exercise"""
        exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not exercise:
            return None
        
        update_data = exercise_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(exercise, key, value)
        
        db.commit()
        db.refresh(exercise)
        logger.info(f"Exercise updated: {exercise_id}")
        return exercise
    
    @staticmethod
    def delete_exercise(db: Session, exercise_id: int) -> bool:
        """Delete an exercise"""
        exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not exercise:
            return False
        
        db.delete(exercise)
        db.commit()
        logger.info(f"Exercise deleted: {exercise_id}")
        return True


class SubmissionService:
    """Exercise submission service"""
    
    @staticmethod
    def create_submission(db: Session, student_id: int, exercise_id: int, code: str, language: str = "python") -> ExerciseSubmission:
        """Create a new submission"""
        submission = ExerciseSubmission(
            student_id=student_id,
            exercise_id=exercise_id,
            code=code,
            language=language,
            status="submitted",
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        logger.info(f"Submission created: {submission.id} by student {student_id}")
        return submission
    
    @staticmethod
    def get_submission(db: Session, submission_id: int) -> Optional[ExerciseSubmission]:
        """Get submission by ID"""
        return db.query(ExerciseSubmission).filter(
            ExerciseSubmission.id == submission_id
        ).first()
    
    @staticmethod
    def get_student_submissions(db: Session, student_id: int, skip: int = 0, limit: int = 100) -> List[ExerciseSubmission]:
        """Get all submissions for a student"""
        return db.query(ExerciseSubmission).filter(
            ExerciseSubmission.student_id == student_id
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_exercise_submissions(db: Session, exercise_id: int, skip: int = 0, limit: int = 100) -> List[ExerciseSubmission]:
        """Get all submissions for an exercise"""
        return db.query(ExerciseSubmission).filter(
            ExerciseSubmission.exercise_id == exercise_id
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_submission_status(db: Session, submission_id: int, status: str, score: Optional[int] = None, feedback: Optional[str] = None) -> Optional[ExerciseSubmission]:
        """Update submission status"""
        submission = db.query(ExerciseSubmission).filter(
            ExerciseSubmission.id == submission_id
        ).first()
        
        if not submission:
            return None
        
        submission.status = status
        if score is not None:
            submission.score = score
        if feedback is not None:
            submission.feedback = feedback
        
        if status == "passing":
            from datetime import datetime
            submission.completed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(submission)
        logger.info(f"Submission updated: {submission_id} - status: {status}")
        return submission


class ProgressService:
    """Student progress tracking service"""
    
    @staticmethod
    def create_progress(db: Session, student_id: int, exercise_id: int) -> Progress:
        """Create progress record"""
        progress = Progress(
            student_id=student_id,
            exercise_id=exercise_id,
            status="in_progress",
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)
        return progress
    
    @staticmethod
    def get_student_progress(db: Session, student_id: int, skip: int = 0, limit: int = 100) -> List[Progress]:
        """Get all progress for a student"""
        return db.query(Progress).filter(
            Progress.student_id == student_id
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_progress(db: Session, student_id: int, exercise_id: int, status: str, score: Optional[int] = None) -> Optional[Progress]:
        """Update progress status"""
        progress = db.query(Progress).filter(
            Progress.student_id == student_id,
            Progress.exercise_id == exercise_id,
        ).first()
        
        if not progress:
            progress = ProgressService.create_progress(db, student_id, exercise_id)
        
        progress.status = status
        progress.attempts += 1
        
        if score is not None and (progress.best_score is None or score > progress.best_score):
            progress.best_score = score
        
        if status == "completed":
            from datetime import datetime
            progress.completed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(progress)
        return progress
    
    @staticmethod
    def get_student_stats(db: Session, student_id: int) -> dict:
        """Get student statistics"""
        total = db.query(Progress).filter(Progress.student_id == student_id).count()
        completed = db.query(Progress).filter(
            Progress.student_id == student_id,
            Progress.status == "completed"
        ).count()
        mastered = db.query(Progress).filter(
            Progress.student_id == student_id,
            Progress.status == "mastered"
        ).count()
        
        avg_score_query = db.query(Progress).filter(
            Progress.student_id == student_id,
            Progress.best_score != None
        ).all()
        
        avg_score = sum(p.best_score for p in avg_score_query) / len(avg_score_query) if avg_score_query else 0
        
        total_attempts = sum(p.attempts for p in db.query(Progress).filter(
            Progress.student_id == student_id
        ).all())
        
        return {
            "total_exercises": total,
            "completed_exercises": completed,
            "mastered_exercises": mastered,
            "average_score": avg_score,
            "total_attempts": total_attempts,
        }
