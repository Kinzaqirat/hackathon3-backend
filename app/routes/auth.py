"""
Authentication endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from app.core.database import get_db
from app.schemas import (
    LoginRequest,
    RegisterRequest,
    PasswordChangeRequest,
    StudentResponse,
    TeacherCreate,
    TeacherResponse,
)
from pydantic import BaseModel
from app.services import AuthService

router = APIRouter(prefix="/api/auth", tags=["authentication"])
logger = logging.getLogger(__name__)

class LoginResponse(BaseModel):
    """Response after login without tokens"""
    user_id: int
    email: str
    role: str
    name: str
    success: bool = True

bearer_scheme = HTTPBearer()


def get_current_user_payload(request: Request) -> Dict[str, Any]:
    """Extract user info from session or header without using complex tokens"""
    # Since we're removing tokens, we'll implement a simple session-based approach
    # For now, we'll use a basic header approach that doesn't involve complex tokens

    # Authentication is required for most endpoints except login/register
    protected_endpoints = [
        "/api/auth/me",
        "/api/auth/change-password",
        "/api/auth/me/teacher",
        "/api/quizzes/teacher",
        "/api/quizzes/",
        "/api/analytics/students",
        "/api/analytics/student/",
        "/api/topics/",
        "/api/exercises",
        "/api/exercises/",
        "/api/chat/sessions",  # Add chat endpoints
        "/api/chat/messages",
    ]

    # Check if the current request is for a protected endpoint
    is_protected = any(request.url.path.startswith(ep) for ep in protected_endpoints) or \
                   any("/teacher" in ep for ep in [request.url.path])

    # Skip authentication for login/register endpoints
    skip_auth_endpoints = ["/api/auth/login", "/api/auth/login/teacher", "/api/auth/register", "/api/auth/register/teacher"]
    should_skip_auth = any(request.url.path.startswith(ep) for ep in skip_auth_endpoints)

    if is_protected and not should_skip_auth:
        # For this simplified approach, we'll use a basic session ID approach
        # In a real implementation, you'd use cookies or server-side sessions
        session_id = request.headers.get("X-Session-ID")

        if not session_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )

        # In a real implementation, you would validate the session ID against a server-side store
        # For this simplified version, we'll simulate extracting user info from the session
        # This is just a placeholder - in reality, you'd look up the session in a database/cache

        # Simulate session validation - in real implementation, validate against server-side storage
        # For demo purposes, we'll parse a simple format: "ROLE|USERID|EMAIL"
        try:
            # Format: "ROLE|USERID|EMAIL" - using pipe delimiter to avoid conflicts with emails
            logger.debug(f"[AUTH] Session ID received: {session_id}")
            parts = session_id.split('|')
            logger.debug(f"[AUTH] Split parts: {parts}, Length: {len(parts)}")
            if len(parts) != 3:
                logger.error(f"[AUTH] Invalid session format - expected 3 parts, got {len(parts)}")
                raise ValueError("Invalid session format")

            role = parts[0]
            user_id = int(parts[1])
            email = parts[2]

            logger.debug(f"[AUTH] Session parsed successfully - Role: {role}, UserID: {user_id}, Email: {email}")

            return {
                "user_id": user_id,
                "email": email,
                "role": role
            }
        except ValueError as ve:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid session: {str(ve)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication"
            )
    else:
        # For non-protected endpoints, return empty payload
        # This avoids authentication checks on login/register endpoints
        return {
            "user_id": 0,
            "email": "",
            "role": "anonymous"
        }


def get_current_user_id(request: Request) -> int:
    """Dependency to get current user ID from the token"""
    payload = get_current_user_payload(request)
    user_id = payload.get("user_id")

    if not user_id or user_id == 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    return user_id


def get_current_user_role(request: Request) -> str:
    """Dependency to get current user role from the token"""
    payload = get_current_user_payload(request)
    role = payload.get("role", "student")

    if role not in ["student", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user role"
        )

    return role


def get_current_teacher_id(request: Request) -> int:
    """Dependency to get current teacher ID from the token"""
    payload = get_current_user_payload(request)
    user_id = payload.get("user_id")
    role = payload.get("role", "student")

    if not user_id or user_id == 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    if role != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Teachers only"
        )

    return user_id


@router.post("/register", response_model=StudentResponse)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """Register a new student"""
    try:
        student = AuthService.register_student(db, request)
        return student
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login student and return user information"""
    try:
        user_info = AuthService.login_student(db, request.email, request.password)
        # Return user info without tokens
        return LoginResponse(
            user_id=user_info["user_id"],
            email=user_info["email"],
            role=user_info["role"],
            name=user_info["name"],
            success=True
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/change-password")
async def change_password(
    request: PasswordChangeRequest,
    db: Session = Depends(get_db),
    payload: Dict[str, Any] = Depends(get_current_user_payload)
):
    """Change password for either student or teacher"""
    try:
        current_user_id = int(payload.get("user_id"))
        role = payload.get("role", "student")  # Default to student for backward compatibility
        AuthService.change_password(
            db,
            current_user_id,
            request.old_password,
            request.new_password,
            role
        )
        return {"message": "Password changed successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )


@router.post("/register/teacher", response_model=TeacherResponse)
async def register_teacher(
    request: TeacherCreate,
    db: Session = Depends(get_db)
):
    """Register a new teacher"""
    try:
        teacher = AuthService.register_teacher(db, request)
        return teacher
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Teacher registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Teacher registration failed"
        )


@router.post("/login/teacher", response_model=LoginResponse)
async def login_teacher(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login teacher and return user information"""
    try:
        user_info = AuthService.login_teacher(db, request.email, request.password)
        # Return user info without tokens
        return LoginResponse(
            user_id=user_info["user_id"],
            email=user_info["email"],
            role=user_info["role"],
            name=user_info["name"],
            success=True
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Teacher login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Teacher login failed"
        )


@router.get("/me", response_model=StudentResponse)
async def get_current_user(
    payload: Dict[str, Any] = Depends(get_current_user_payload),
    db: Session = Depends(get_db)
):
    """Get current user profile"""
    try:
        user_id = int(payload.get("user_id"))
        role = payload.get("role", "student")  # Default to student for backward compatibility

        if role == "student":
            student = AuthService.get_student_by_id(db, user_id)
            if not student:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Student not found"
                )
            return student
        elif role == "teacher":
            teacher = AuthService.get_teacher_by_id(db, user_id)
            if not teacher:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Teacher not found"
                )
            # Convert teacher to a compatible response format
            return StudentResponse(
                id=teacher.id,
                email=teacher.email,
                name=teacher.name,
                grade_level=teacher.department or "",
                bio=teacher.bio,
                avatar_url=teacher.avatar_url,
                is_active=teacher.is_active,
                created_at=teacher.created_at,
                user_id=teacher.user_id
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unknown user role"
            )
    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )


@router.get("/me/teacher", response_model=TeacherResponse)
async def get_current_teacher(
    payload: Dict[str, Any] = Depends(get_current_user_payload),
    db: Session = Depends(get_db)
):
    """Get current teacher profile"""
    try:
        user_id = int(payload.get("user_id"))
        role = payload.get("role")

        if role != "teacher":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Teachers only"
            )

        teacher = AuthService.get_teacher_by_id(db, user_id)
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher not found"
            )
        return teacher
    except Exception as e:
        logger.error(f"Get teacher error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get teacher profile"
        )
