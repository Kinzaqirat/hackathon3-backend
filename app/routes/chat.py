"""
Chat endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocketDisconnect, WebSocket, Request
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.schemas import ChatSessionResponse, ChatMessageResponse, ChatMessageCreate
from app.services import ChatService
from app.services.kafka_service import KafkaService
from app.routes.auth import get_current_user_payload

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = logging.getLogger(__name__)


@router.post("/sessions/", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    request: Request,
    student_id: int,
    topic: str = Query(None),
    agent_type: str = Query("general"),
    db: Session = Depends(get_db)
):
    """Create a new chat session"""
    try:
        # Get current user info
        current_user = get_current_user_payload(request)
        current_user_id = current_user.get("user_id")
        current_role = current_user.get("role")

        logger.info(f"[CHAT] Create session - current_user_id: {current_user_id} (type: {type(current_user_id)}), student_id: {student_id} (type: {type(student_id)}), role: {current_role}")

        # Only students can create chat sessions for themselves
        if current_role != "student" or current_user_id != student_id:
            logger.warning(f"[CHAT] Access denied - role check: {current_role == 'student'}, user_id check: {current_user_id == student_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Students can only create chat sessions for themselves"
            )

        session = ChatService.create_chat_session(db, student_id, topic, agent_type)

        await KafkaService.publish_chat_message(
            session.id,
            student_id,
            "system",
            f"Chat session created with {agent_type} agent"
        )

        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create chat session error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create chat session"
        )


@router.get("/sessions/{student_id}", response_model=list[ChatSessionResponse])
async def get_chat_sessions(
    student_id: int,
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all chat sessions for a student"""
    try:
        # Get current user info
        current_user = get_current_user_payload(request)
        current_user_id = current_user.get("user_id")
        current_role = current_user.get("role")

        # Students can only access their own chat sessions
        # Teachers can access any student's chat sessions
        if current_role == "student" and current_user_id != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Cannot access other students' chat sessions"
            )

        return ChatService.get_student_chat_sessions(db, student_id, skip, limit)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get chat sessions error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get chat sessions"
        )


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageResponse])
async def get_chat_messages(
    session_id: int,
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all messages in a chat session"""
    try:
        # Get current user info
        current_user = get_current_user_payload(request)
        current_user_id = current_user.get("user_id")
        current_role = current_user.get("role")

        session = ChatService.get_chat_session(db, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )

        # Students can only access messages from their own sessions
        # Teachers can access any session's messages
        if current_role == "student" and session.student_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Cannot access messages from other students' sessions"
            )

        return ChatService.get_session_messages(db, session_id, skip, limit)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get chat messages error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get chat messages"
        )


@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
async def send_chat_message(
    session_id: int,
    message: ChatMessageCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Send a message in a chat session"""
    try:
        # Get current user info
        current_user = get_current_user_payload(request)
        current_user_id = current_user.get("user_id")
        current_role = current_user.get("role")

        session = ChatService.get_chat_session(db, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )

        # Only the student who owns the session can send messages
        if current_role != "student" or session.student_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Only the session owner can send messages"
            )

        if not session.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chat session is not active"
            )

        # Add user message
        user_message = ChatService.add_message(
            db,
            session_id,
            "user",
            message.content,
            message.message_metadata
        )

        # Publish message to Kafka
        await KafkaService.publish_chat_message(
            session_id,
            session.student_id,
            "user",
            message.content
        )

        # Generate agent response (synchronous for hackathon/testing simplicity)
        await ChatService.generate_agent_response(db, session_id)

        return user_message
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Send message error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message"
        )


@router.put("/sessions/{session_id}/end")
async def end_chat_session(
    session_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """End a chat session"""
    try:
        # Get current user info
        current_user = get_current_user_payload(request)
        current_user_id = current_user.get("user_id")
        current_role = current_user.get("role")

        session = ChatService.get_chat_session(db, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )

        # Only the student who owns the session can end it
        if current_role != "student" or session.student_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Only the session owner can end the session"
            )

        session = ChatService.end_chat_session(db, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )

        await KafkaService.publish_chat_message(
            session_id,
            session.student_id,
            "system",
            "Chat session ended"
        )

        return {"message": "Chat session ended"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"End session error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to end session"
        )


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: int, db: Session = Depends(get_db)):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for now - implement real chat logic here
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        logger.info(f"Client disconnected from session {session_id}")
