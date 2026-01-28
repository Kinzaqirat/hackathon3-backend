"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# ============= Level Schemas =============
class LevelBase(BaseModel):
    name: str
    description: Optional[str] = None
    order: int = 0


class LevelCreate(LevelBase):
    pass


class LevelResponse(LevelBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


# ============= Topic Schemas =============
class TopicBase(BaseModel):
    name: str
    description: Optional[str] = None
    level_id: int
    order: int = 0
    learning_objectives: Optional[List[str]] = None
    resources: Optional[List[Dict[str, str]]] = None


class TopicCreate(TopicBase):
    pass


class TopicUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    level_id: Optional[int] = None
    order: Optional[int] = None
    learning_objectives: Optional[List[str]] = None
    resources: Optional[List[Dict[str, str]]] = None


class TopicResponse(TopicBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


# ============= Quiz Schemas =============
class QuizQuestionBase(BaseModel):
    question_text: str
    question_type: str = "multiple_choice"  # multiple_choice, true_false, short_answer, code
    options: Optional[List[str]] = None
    correct_answer: Optional[Any] = None
    explanation: Optional[str] = None
    order: int = 0
    points: int = 1


class QuizQuestionCreate(QuizQuestionBase):
    pass


class QuizQuestionResponse(QuizQuestionBase):
    id: int
    quiz_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class QuizBase(BaseModel):
    title: str
    description: Optional[str] = None
    topic_id: int
    level_id: int
    teacher_id: Optional[int] = None
    passing_score: int = 70
    time_limit_minutes: Optional[int] = None
    shuffle_questions: bool = True


class QuizCreate(QuizBase):
    questions: Optional[List[QuizQuestionCreate]] = None


class QuizUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    passing_score: Optional[int] = None
    time_limit_minutes: Optional[int] = None
    shuffle_questions: Optional[bool] = None


class QuizResponse(QuizBase):
    id: int
    created_at: datetime
    updated_at: datetime
    questions: Optional[List[QuizQuestionResponse]] = None
    
    # Enrichment fields for teacher dashboard
    student_count: Optional[int] = None
    completed_count: Optional[int] = None
    avg_score: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)


class QuizAnswerCreate(BaseModel):
    question_id: int
    answer_text: Any  # Can be string, list, object, or boolean


class QuizAnswerResponse(BaseModel):
    id: int
    question_id: int
    answer_text: Any
    is_correct: bool
    points_earned: int
    answered_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuizSubmissionCreate(BaseModel):
    quiz_id: int


class QuizSubmissionResponse(BaseModel):
    id: int
    student_id: int
    quiz_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    score: Optional[int] = None
    passed: bool
    answers: Optional[List[QuizAnswerResponse]] = None

    model_config = ConfigDict(from_attributes=True)


# ============= Existing Schemas =============
class StudentBase(BaseModel):
    email: EmailStr
    name: str
    grade_level: Optional[str] = None
    bio: Optional[str] = None


class StudentCreate(StudentBase):
    password: str


class StudentResponse(StudentBase):
    id: int
    user_id: UUID
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ExerciseBase(BaseModel):
    title: str
    description: str
    difficulty_level: str
    topic: str


class ExerciseCreate(ExerciseBase):
    starter_code: Optional[str] = None
    expected_output: Optional[str] = None
    test_cases: Optional[List[Dict[str, Any]]] = None
    hints: Optional[List[str]] = None
    solution_code: Optional[str] = None


class ExerciseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty_level: Optional[str] = None
    topic: Optional[str] = None
    starter_code: Optional[str] = None
    expected_output: Optional[str] = None
    test_cases: Optional[List[Dict[str, Any]]] = None
    hints: Optional[List[str]] = None
    solution_code: Optional[str] = None


class ExerciseResponse(ExerciseBase):
    id: int
    starter_code: Optional[str] = None
    expected_output: Optional[str] = None
    test_cases: Optional[List[Dict[str, Any]]] = None
    hints: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class SubmissionBase(BaseModel):
    student_id: int
    exercise_id: int
    code: str
    language: str = "python"


class SubmissionCreate(SubmissionBase):
    pass


class SubmissionResponse(SubmissionBase):
    id: int
    status: str
    score: Optional[int] = None
    feedback: Optional[str] = None
    submitted_at: datetime
    completed_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class CodeExecutionResultResponse(BaseModel):
    """Code execution result response"""
    id: int
    submission_id: int
    execution_result: Dict[str, Any]
    passed: bool
    duration_ms: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProgressResponse(BaseModel):
    id: int
    student_id: int
    exercise_id: int
    status: str
    attempts: int = 0
    best_score: Optional[int] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ChatSessionResponse(BaseModel):
    id: int
    student_id: int
    session_id: UUID
    topic: Optional[str] = None
    agent_type: str
    is_active: bool
    created_at: datetime
    ended_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ChatMessageResponse(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    message_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatMessageCreate(BaseModel):
    """Chat message creation request"""
    session_id: int
    role: str
    content: str
    message_metadata: Optional[Dict[str, Any]] = None


class TokenResponse(BaseModel):
    """Token response after authentication"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    
    model_config = ConfigDict(from_attributes=True)


class TokenRefreshRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class LoginRequest(BaseModel):
    """Login request"""
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Register request"""
    email: EmailStr
    name: str
    password: str
    grade_level: Optional[str] = None


class PasswordChangeRequest(BaseModel):
    """Password change request"""
    old_password: str
    new_password: str


class TeacherBase(BaseModel):
    email: EmailStr
    name: str
    department: Optional[str] = None
    bio: Optional[str] = None


class TeacherCreate(TeacherBase):
    password: str


class TeacherResponse(TeacherBase):
    id: int
    user_id: UUID
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentStats(BaseModel):
    """Student statistics"""
    student_id: int
    total_exercises: int
    completed_exercises: int
    average_score: float
    total_time_spent_minutes: int
    last_activity: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ExerciseStats(BaseModel):
    """Exercise statistics"""
    exercise_id: int
    total_attempts: int
    successful_attempts: int
    average_score: float
    average_time_minutes: float

    model_config = ConfigDict(from_attributes=True)
