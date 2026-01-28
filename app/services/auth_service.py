"""
Authentication service - Simplified version without tokens
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging

from app.models import Student, Teacher
from app.core.security import hash_password, verify_password
from app.schemas import StudentCreate, TeacherCreate
from typing import Dict, Any

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service - simplified without tokens"""

    @staticmethod
    def register_student(db: Session, student_data: StudentCreate) -> Student:
        """Register a new student"""
        # Check if email already exists
        existing_student = db.query(Student).filter(
            Student.email == student_data.email
        ).first()

        if existing_student:
            raise ValueError("Email already registered")

        # Create new student
        db_student = Student(
            email=student_data.email,
            name=student_data.name,
            password_hash=hash_password(student_data.password),
            grade_level=student_data.grade_level,
        )

        try:
            db.add(db_student)
            db.commit()
            db.refresh(db_student)
            logger.info(f"Student registered: {db_student.email}")
            return db_student
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Registration error: {str(e)}")
            raise ValueError("Email already registered")

    @staticmethod
    def register_teacher(db: Session, teacher_data: TeacherCreate) -> Teacher:
        """Register a new teacher"""
        # Check if email already exists
        existing_teacher = db.query(Teacher).filter(
            Teacher.email == teacher_data.email
        ).first()

        if existing_teacher:
            raise ValueError("Email already registered")

        # Create new teacher
        db_teacher = Teacher(
            email=teacher_data.email,
            name=teacher_data.name,
            password_hash=hash_password(teacher_data.password),
            department=teacher_data.department,
            bio=teacher_data.bio,
        )

        try:
            db.add(db_teacher)
            db.commit()
            db.refresh(db_teacher)
            logger.info(f"Teacher registered: {db_teacher.email}")
            return db_teacher
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Teacher registration error: {str(e)}")
            raise ValueError("Email already registered")

    @staticmethod
    def login_student(db: Session, email: str, password: str) -> Dict[str, Any]:
        """Login student and return user information"""
        student = db.query(Student).filter(Student.email == email).first()

        if not student:
            logger.warning(f"Login attempt with non-existent email: {email}")
            raise ValueError("Invalid email or password")

        if not verify_password(password, student.password_hash):
            logger.warning(f"Failed login attempt for: {email}")
            raise ValueError("Invalid email or password")

        if not student.is_active:
            raise ValueError("Student account is inactive")

        logger.info(f"Student logged in: {email}")

        # Return user information without tokens
        return {
            "user_id": student.id,
            "email": student.email,
            "role": "student",
            "name": student.name
        }

    @staticmethod
    def login_teacher(db: Session, email: str, password: str) -> Dict[str, Any]:
        """Login teacher and return user information"""
        teacher = db.query(Teacher).filter(Teacher.email == email).first()

        if not teacher:
            logger.warning(f"Login attempt with non-existent email: {email}")
            raise ValueError("Invalid email or password")

        if not verify_password(password, teacher.password_hash):
            logger.warning(f"Failed login attempt for: {email}")
            raise ValueError("Invalid email or password")

        if not teacher.is_active:
            raise ValueError("Teacher account is inactive")

        logger.info(f"Teacher logged in: {email}")

        # Return user information without tokens
        return {
            "user_id": teacher.id,
            "email": teacher.email,
            "role": "teacher",
            "name": teacher.name
        }

    @staticmethod
    def get_student_by_email(db: Session, email: str) -> Student:
        """Get student by email"""
        return db.query(Student).filter(Student.email == email).first()

    @staticmethod
    def get_student_by_id(db: Session, student_id: int) -> Student:
        """Get student by ID"""
        return db.query(Student).filter(Student.id == student_id).first()

    @staticmethod
    def get_teacher_by_email(db: Session, email: str) -> Teacher:
        """Get teacher by email"""
        return db.query(Teacher).filter(Teacher.email == email).first()

    @staticmethod
    def get_teacher_by_id(db: Session, teacher_id: int) -> Teacher:
        """Get teacher by ID"""
        return db.query(Teacher).filter(Teacher.id == teacher_id).first()

    @staticmethod
    def change_password(db: Session, user_id: int, old_password: str, new_password: str, role: str) -> bool:
        """Change password for either student or teacher"""
        if role == "student":
            user = db.query(Student).filter(Student.id == user_id).first()
        elif role == "teacher":
            user = db.query(Teacher).filter(Teacher.id == user_id).first()
        else:
            raise ValueError("Invalid role")

        if not user:
            raise ValueError("User not found")

        if not verify_password(old_password, user.password_hash):
            raise ValueError("Old password is incorrect")

        user.password_hash = hash_password(new_password)
        db.commit()
        logger.info(f"Password changed for {role}: {user.email}")
        return True
