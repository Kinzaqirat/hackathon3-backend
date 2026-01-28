"""
Kafka service for event streaming
"""

import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime
from aiokafka import AIOKafkaProducer
from app.core.config import settings

logger = logging.getLogger(__name__)


class KafkaService:
    """Kafka event streaming service"""
    
    _producer: Optional[AIOKafkaProducer] = None
    _is_disabled: bool = False
    
    @classmethod
    async def get_producer(cls) -> Optional[AIOKafkaProducer]:
        """Get or create Kafka producer"""
        if cls._is_disabled:
            return None
            
        if cls._producer is None:
            try:
                cls._producer = AIOKafkaProducer(
                    bootstrap_servers=settings.kafka_bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    request_timeout_ms=1000,
                    retry_backoff_ms=500
                )
                await cls._producer.start()
                logger.info("Kafka producer started")
            except Exception as e:
                logger.warning(f"Could not connect to Kafka: {str(e)}. Event streaming will be disabled.")
                cls._is_disabled = True
                cls._producer = None
                return None
        return cls._producer
    
    @classmethod
    async def close_producer(cls):
        """Close Kafka producer"""
        if cls._producer is not None:
            try:
                await cls._producer.stop()
            except Exception:
                pass
            cls._producer = None
            logger.info("Kafka producer closed")
    
    @classmethod
    async def publish_event(cls, topic: str, event: Dict[str, Any], key: str = None):
        """Publish an event to Kafka"""
        try:
            producer = await cls.get_producer()
            if producer is None:
                logger.debug(f"Kafka disabled, skipping event to {topic}")
                return
                
            await producer.send_and_wait(
                topic,
                value=event,
                key=key.encode('utf-8') if key else None
            )
            logger.debug(f"Event published to {topic}: {key}")
        except Exception as e:
            logger.error(f"Error publishing to {topic}: {str(e)}")
            # Do not raise here to keep the application running
    
    @classmethod
    async def publish_student_event(cls, student_id: int, event_type: str, data: Dict[str, Any]):
        """Publish a student event"""
        event = {
            "event_type": event_type,
            "student_id": student_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        await cls.publish_event("student-events", event, key=str(student_id))
    
    @classmethod
    async def publish_submission_event(cls, student_id: int, exercise_id: int, submission_id: int, status: str):
        """Publish exercise submission event"""
        event = {
            "event_type": "submission",
            "student_id": student_id,
            "exercise_id": exercise_id,
            "submission_id": submission_id,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await cls.publish_event("exercise-submissions", event, key=str(submission_id))
    
    @classmethod
    async def publish_progress_event(cls, student_id: int, exercise_id: int, status: str, score: int = None):
        """Publish progress update event"""
        event = {
            "event_type": "progress_update",
            "student_id": student_id,
            "exercise_id": exercise_id,
            "status": status,
            "score": score,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await cls.publish_event("progress-updates", event, key=f"{student_id}:{exercise_id}")
    
    @classmethod
    async def publish_chat_message(cls, session_id: int, student_id: int, role: str, content: str):
        """Publish chat message event"""
        event = {
            "event_type": "chat_message",
            "session_id": session_id,
            "student_id": student_id,
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await cls.publish_event("chat-messages", event, key=str(session_id))
    
    @classmethod
    async def publish_system_event(cls, component: str, event_type: str, severity: str = "info", details: Dict[str, Any] = None):
        """Publish system event"""
        event = {
            "event_type": event_type,
            "component": component,
            "severity": severity,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat(),
        }
        await cls.publish_event("system-events", event, key=component)
