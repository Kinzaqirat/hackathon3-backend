"""
Quiz endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.core.database import get_db
from app.models.models import (
    Quiz, QuizQuestion, QuizSubmission, QuizAnswer, Student
)
from app.schemas import (
    QuizCreate, QuizResponse, QuizUpdate,
    QuizSubmissionCreate, QuizSubmissionResponse,
    QuizAnswerCreate, QuizAnswerResponse
)
from app.routes.auth import get_current_user_payload, get_current_teacher_id

router = APIRouter(prefix="/api/quizzes", tags=["quizzes"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def create_quiz(
    quiz: QuizCreate,
    current_teacher_id: int = Depends(get_current_teacher_id),
    db: Session = Depends(get_db)
):
    """Create a new quiz (Teachers only)"""
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


@router.get("/", response_model=list[QuizResponse])
async def list_quizzes(
    request: Request,
    topic_id: int = Query(None),
    level_id: int = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List quizzes with optional filtering"""
    try:
        # Check if user is authenticated
        current_user = get_current_user_payload(request)
        current_user_id = current_user.get("user_id")

        if not current_user_id or current_user_id == 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )

        query = db.query(Quiz)

        if topic_id:
            query = query.filter(Quiz.topic_id == topic_id)
        if level_id:
            query = query.filter(Quiz.level_id == level_id)

        quizzes = query.offset(skip).limit(limit).all()
        return quizzes
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List quizzes error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch quizzes"
        )


@router.get("/{quiz_id}", response_model=QuizResponse)
async def get_quiz(
    request: Request,
    quiz_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific quiz"""
    try:
        # Check if user is authenticated
        current_user = get_current_user_payload(request)
        current_user_id = current_user.get("user_id")

        if not current_user_id or current_user_id == 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )

        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )
        return quiz
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get quiz error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch quiz"
        )


@router.put("/{quiz_id}", response_model=QuizResponse)
async def update_quiz(
    quiz_id: int,
    quiz_update: QuizUpdate,
    current_teacher_id: int = Depends(get_current_teacher_id),
    db: Session = Depends(get_db)
):
    """Update a quiz (Teachers only)"""
    try:
        db_quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not db_quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )

        # Verify that the current teacher owns this quiz
        if db_quiz.teacher_id != current_teacher_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only update your own quizzes"
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


@router.delete("/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quiz(
    quiz_id: int,
    current_teacher_id: int = Depends(get_current_teacher_id),
    db: Session = Depends(get_db)
):
    """Delete a quiz (Teachers only)"""
    try:
        db_quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not db_quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )

        # Verify that the current teacher owns this quiz
        if db_quiz.teacher_id != current_teacher_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only delete your own quizzes"
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


# ============= Quiz Submission Endpoints =============

@router.post("/{quiz_id}/start", response_model=QuizSubmissionResponse, status_code=status.HTTP_201_CREATED)
async def start_quiz(
    quiz_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Start a quiz submission"""
    try:
        from app.routes.auth import get_current_user_payload

        # Get current user info
        current_user = get_current_user_payload(request)
        current_user_id = current_user.get("user_id")
        current_role = current_user.get("role")

        # Only students can start quizzes
        if current_role != "student":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only students can start quizzes"
            )

        # Verify quiz exists
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )

        # Verify student exists
        student = db.query(Student).filter(Student.id == current_user_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )

        # Create submission
        submission = QuizSubmission(
            student_id=current_user_id,
            quiz_id=quiz_id
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        return submission
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Start quiz error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start quiz"
        )


@router.post("/{quiz_id}/submissions/{submission_id}/answer", response_model=QuizAnswerResponse, status_code=status.HTTP_201_CREATED)
async def submit_answer(
    quiz_id: int,
    submission_id: int,
    answer: QuizAnswerCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Submit an answer to a quiz question"""
    try:
        from app.routes.auth import get_current_user_payload

        # Get current user info
        current_user = get_current_user_payload(request)
        current_user_id = current_user.get("user_id")
        current_role = current_user.get("role")

        # Only students can submit answers
        if current_role != "student":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only students can submit answers"
            )

        # Verify submission exists and belongs to current student
        submission = db.query(QuizSubmission).filter(
            QuizSubmission.id == submission_id,
            QuizSubmission.student_id == current_user_id
        ).first()
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found or does not belong to current student"
            )

        # Verify question exists and belongs to quiz
        question = db.query(QuizQuestion).filter(
            QuizQuestion.id == answer.question_id,
            QuizQuestion.quiz_id == quiz_id
        ).first()
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )

        # Check if answer already exists
        existing_answer = db.query(QuizAnswer).filter(
            QuizAnswer.submission_id == submission_id,
            QuizAnswer.question_id == answer.question_id
        ).first()

        if existing_answer:
            db.delete(existing_answer)

        # Determine if answer is correct
        is_correct = False
        points_earned = 0

        if question.question_type == "multiple_choice":
            is_correct = answer.answer_text == question.correct_answer
        elif question.question_type == "true_false":
            is_correct = answer.answer_text == question.correct_answer
        elif question.question_type == "short_answer":
            # Simple string comparison (can be enhanced with NLP)
            is_correct = str(answer.answer_text).lower().strip() == str(question.correct_answer).lower().strip()

        if is_correct:
            points_earned = question.points

        # Create answer
        db_answer = QuizAnswer(
            submission_id=submission_id,
            question_id=answer.question_id,
            answer_text=answer.answer_text,
            is_correct=is_correct,
            points_earned=points_earned
        )
        db.add(db_answer)
        db.commit()
        db.refresh(db_answer)
        return db_answer
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Submit answer error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit answer"
        )


@router.post("/{quiz_id}/submissions/{submission_id}/complete", response_model=QuizSubmissionResponse)
async def complete_quiz(
    quiz_id: int,
    submission_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Complete and score a quiz submission"""
    try:
        from app.routes.auth import get_current_user_payload

        # Get current user info
        current_user = get_current_user_payload(request)
        current_user_id = current_user.get("user_id")
        current_role = current_user.get("role")

        # Only students can complete quizzes
        if current_role != "student":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only students can complete quizzes"
            )

        # Verify submission exists and belongs to current student
        submission = db.query(QuizSubmission).filter(
            QuizSubmission.id == submission_id,
            QuizSubmission.student_id == current_user_id
        ).first()
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found or does not belong to current student"
            )

        # Get quiz
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )

        # Calculate score
        all_answers = db.query(QuizAnswer).filter(
            QuizAnswer.submission_id == submission_id
        ).all()

        total_points = sum(a.points_earned for a in all_answers)
        max_points = db.query(QuizQuestion).filter(
            QuizQuestion.quiz_id == quiz_id
        ).with_entities(QuizQuestion.points).all()

        max_score = sum(p[0] for p in max_points) or 1  # Avoid division by zero
        score = int((total_points / max_score) * 100)

        # Update submission
        submission.completed_at = datetime.utcnow()
        submission.score = score
        submission.passed = score >= quiz.passing_score

        db.commit()
        db.refresh(submission)
        return submission
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Complete quiz error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete quiz"
        )


@router.get("/{quiz_id}/submissions/{submission_id}", response_model=QuizSubmissionResponse)
async def get_submission(
    quiz_id: int,
    submission_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get a quiz submission"""
    try:
        from app.routes.auth import get_current_user_payload

        # Get current user info
        current_user = get_current_user_payload(request)
        current_user_id = current_user.get("user_id")
        current_role = current_user.get("role")

        # Students can only access their own submissions
        # Teachers can access any submission for their quizzes
        if current_role == "student":
            submission = db.query(QuizSubmission).filter(
                QuizSubmission.id == submission_id,
                QuizSubmission.quiz_id == quiz_id,
                QuizSubmission.student_id == current_user_id
            ).first()
        elif current_role == "teacher":
            # Check if the quiz belongs to this teacher
            quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.teacher_id == current_user_id).first()
            if not quiz:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: You can only access submissions for your quizzes"
                )
            submission = db.query(QuizSubmission).filter(
                QuizSubmission.id == submission_id,
                QuizSubmission.quiz_id == quiz_id
            ).first()
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )
        return submission
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get submission error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch submission"
        )


@router.get("/teacher", response_model=list[dict])
async def get_teacher_quizzes(
    current_teacher_id: int = Depends(get_current_teacher_id),
    db: Session = Depends(get_db)
):
    """Get all quizzes created by the current teacher with statistics"""
    try:
        from sqlalchemy import func
        # Get all quizzes created by this teacher
        quizzes = db.query(Quiz).filter(Quiz.teacher_id == current_teacher_id).all()
        
        result = []
        for quiz in quizzes:
            # Stats for this quiz
            total_submissions = db.query(QuizSubmission).filter(QuizSubmission.quiz_id == quiz.id).count()
            completed_submissions = db.query(QuizSubmission).filter(
                QuizSubmission.quiz_id == quiz.id,
                QuizSubmission.completed_at != None
            ).count()
            
            avg_score = db.query(func.avg(QuizSubmission.score)).filter(
                QuizSubmission.quiz_id == quiz.id,
                QuizSubmission.score != None
            ).scalar() or 0
            
            # For student count, we might want to know how many students are assigned or total students
            # Let's say it's total students for now as a baseline
            total_students = db.query(Student).count()
            
            quiz_dict = {
                "id": quiz.id,
                "title": quiz.title,
                "description": quiz.description,
                "topic_id": quiz.topic_id,
                "level_id": quiz.level_id,
                "teacher_id": quiz.teacher_id,
                "passing_score": quiz.passing_score,
                "time_limit_minutes": quiz.time_limit_minutes,
                "shuffle_questions": quiz.shuffle_questions,
                "created_at": quiz.created_at,
                "updated_at": quiz.updated_at,
                "student_count": total_students,
                "completed_count": completed_submissions,
                "avg_score": round(float(avg_score), 1)
            }
            result.append(quiz_dict)
            
        return result
    except Exception as e:
        logger.error(f"Get teacher quizzes error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch teacher quizzes with stats"
        )
