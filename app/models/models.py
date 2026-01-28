"""
SQLAlchemy models for LearnFlow
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, UUID, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class Level(Base):
    """Skill levels (Beginner, Intermediate, Advanced)"""
    __tablename__ = "levels"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # Beginner, Intermediate, Advanced, Expert
    description = Column(Text, nullable=True)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    topics = relationship("Topic", back_populates="level")
    exercises = relationship("Exercise", back_populates="level")


class Topic(Base):
    """Python topics/modules"""
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    level_id = Column(Integer, ForeignKey("levels.id"), nullable=False)
    order = Column(Integer, default=0)
    learning_objectives = Column(JSON, nullable=True)  # Array of learning objectives
    resources = Column(JSON, nullable=True)  # Array of resource links
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    level = relationship("Level", back_populates="topics")
    exercises = relationship("Exercise", back_populates="topic_rel")


class Student(Base):
    """Student user model"""
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    grade_level = Column(String(50), nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    submissions = relationship("ExerciseSubmission", back_populates="student")
    progress = relationship("Progress", back_populates="student")
    chat_sessions = relationship("ChatSession", back_populates="student")


class Exercise(Base):
    """Exercise/Problem model"""
    __tablename__ = "exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    difficulty_level = Column(String(50), default="medium")  # easy, medium, hard
    topic = Column(String(100), nullable=False, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    level_id = Column(Integer, ForeignKey("levels.id"), nullable=True)
    starter_code = Column(Text, nullable=True)
    expected_output = Column(Text, nullable=True)
    test_cases = Column(JSON, nullable=True)  # Array of test cases
    hints = Column(JSON, nullable=True)  # Array of hints
    solution_code = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    submissions = relationship("ExerciseSubmission", back_populates="exercise")
    progress = relationship("Progress", back_populates="exercise")
    topic_rel = relationship("Topic", back_populates="exercises")
    level = relationship("Level", back_populates="exercises")


class ExerciseSubmission(Base):
    """Student exercise submission model"""
    __tablename__ = "exercise_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    code = Column(Text, nullable=False)
    language = Column(String(50), default="python")
    status = Column(String(50), default="submitted")  # draft, submitted, passing, failing
    score = Column(Integer, nullable=True)  # 0-100
    feedback = Column(Text, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    student = relationship("Student", back_populates="submissions")
    exercise = relationship("Exercise", back_populates="submissions")
    execution_results = relationship("CodeExecutionResult", back_populates="submission")


class CodeExecutionResult(Base):
    """Results from code execution"""
    __tablename__ = "code_execution_results"
    
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("exercise_submissions.id"), nullable=False)
    execution_result = Column(JSON, nullable=False)  # stdout, stderr, etc.
    passed = Column(Boolean, default=False)
    duration_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    submission = relationship("ExerciseSubmission", back_populates="execution_results")


class Progress(Base):
    """Student progress tracking"""
    __tablename__ = "progress"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    status = Column(String(50), default="not_started")  # not_started, in_progress, completed, mastered
    attempts = Column(Integer, default=0)
    best_score = Column(Integer, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="progress")
    exercise = relationship("Exercise", back_populates="progress")


class ChatSession(Base):
    """Chat session between student and AI agent"""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    session_id = Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4)
    topic = Column(String(100), nullable=True)
    agent_type = Column(String(50), default="general")  # concepts, debug, exercise, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    
    # Relationships
    student = relationship("Student", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON, nullable=True)  # Changed from 'metadata'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # ...existing code...
    session = relationship("ChatSession", back_populates="messages")

class Teacher(Base):
    """Teacher user model"""
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    department = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    created_quizzes = relationship("Quiz", back_populates="creator")


class SystemEvent(Base):
    """System and infrastructure events"""
    __tablename__ = "system_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    component = Column(String(100), nullable=False)
    severity = Column(String(50), default="info")  # info, warning, error
    details = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class Quiz(Base):
    """Quiz model"""
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    level_id = Column(Integer, ForeignKey("levels.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=True)  # Nullable for backward compatibility
    passing_score = Column(Integer, default=70)  # Percentage
    time_limit_minutes = Column(Integer, nullable=True)
    shuffle_questions = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")
    submissions = relationship("QuizSubmission", back_populates="quiz", cascade="all, delete-orphan")
    topic = relationship("Topic")
    level = relationship("Level")
    creator = relationship("Teacher", back_populates="created_quizzes")


class QuizQuestion(Base):
    """Quiz question model"""
    __tablename__ = "quiz_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), default="multiple_choice")  # multiple_choice, true_false, short_answer, code
    options = Column(JSON, nullable=True)  # Array of options for multiple choice
    correct_answer = Column(JSON, nullable=True)  # Can be string, list, or object
    explanation = Column(Text, nullable=True)
    order = Column(Integer, default=0)
    points = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    answers = relationship("QuizAnswer", back_populates="question", cascade="all, delete-orphan")


class QuizSubmission(Base):
    """Student's quiz submission"""
    __tablename__ = "quiz_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    score = Column(Integer, nullable=True)  # 0-100
    passed = Column(Boolean, default=False)
    
    # Relationships
    student = relationship("Student")
    quiz = relationship("Quiz", back_populates="submissions")
    answers = relationship("QuizAnswer", back_populates="submission", cascade="all, delete-orphan")


class QuizAnswer(Base):
    """Individual answer to a quiz question"""
    __tablename__ = "quiz_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("quiz_submissions.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("quiz_questions.id"), nullable=False)
    answer_text = Column(JSON, nullable=False)  # JSON to support various answer types
    is_correct = Column(Boolean, default=False)
    points_earned = Column(Integer, default=0)
    answered_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    submission = relationship("QuizSubmission", back_populates="answers")
    question = relationship("QuizQuestion", back_populates="answers")
