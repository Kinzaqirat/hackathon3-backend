"""
Chat service
"""

from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime
import json

from app.models import ChatSession, ChatMessage

logger = logging.getLogger(__name__)


class ChatService:
    """Chat service for student-agent interactions"""
    
    @staticmethod
    def create_chat_session(db: Session, student_id: int, topic: Optional[str] = None, agent_type: str = "general") -> ChatSession:
        """Create a new chat session"""
        session = ChatSession(
            student_id=student_id,
            topic=topic,
            agent_type=agent_type,
            is_active=True,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        logger.info(f"Chat session created: {session.id} for student {student_id}")
        return session
    
    @staticmethod
    def get_chat_session(db: Session, session_id: int) -> Optional[ChatSession]:
        """Get chat session by ID"""
        return db.query(ChatSession).filter(ChatSession.id == session_id).first()
    
    @staticmethod
    def get_student_chat_sessions(db: Session, student_id: int, skip: int = 0, limit: int = 100) -> List[ChatSession]:
        """Get all chat sessions for a student"""
        return db.query(ChatSession).filter(
            ChatSession.student_id == student_id
        ).order_by(ChatSession.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def end_chat_session(db: Session, session_id: int) -> Optional[ChatSession]:
        """End a chat session"""
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            return None
        
        session.is_active = False
        session.ended_at = datetime.utcnow()
        db.commit()
        db.refresh(session)
        logger.info(f"Chat session ended: {session_id}")
        return session
    
    @staticmethod
    def add_message(db: Session, session_id: int, role: str, content: str, metadata: Optional[dict] = None) -> ChatMessage:
        """Add message to chat session"""
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            message_metadata=metadata or {},
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        logger.debug(f"Message added to session {session_id}: {role}")
        return message
    
    @staticmethod
    def get_session_messages(db: Session, session_id: int, skip: int = 0, limit: int = 100) -> List[ChatMessage]:
        """Get all messages in a chat session"""
        return db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_recent_context(db: Session, session_id: int, context_length: int = 10) -> List[dict]:
        """Get recent messages for context"""
        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at.desc()).limit(context_length).all()
        
        # Reverse to get chronological order
        messages.reverse()
        
        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

    @staticmethod
    async def generate_agent_response(db: Session, session_id: int) -> Optional[ChatMessage]:
        """Generate and save AI agent response"""
        from app.services.ai_service import AIService
        from app.services.kafka_service import KafkaService

        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session or not session.is_active:
            return None

        # Get context
        context = ChatService.get_recent_context(db, session_id)
        
        # Generate response
        response_text = await AIService.generate_response(context, session.agent_type)
        
        # Save response
        agent_message = ChatService.add_message(
            db,
            session_id,
            "assistant",
            response_text
        )
        
        # Publish to Kafka
        await KafkaService.publish_chat_message(
            session_id,
            session.student_id,
            "assistant",
            response_text
        )
        
        return agent_message
