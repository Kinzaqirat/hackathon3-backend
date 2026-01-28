"""
Initialize services module
"""

from app.services.auth_service import AuthService
from app.services.exercise_service import ExerciseService, SubmissionService, ProgressService
from app.services.chat_service import ChatService
from app.services.kafka_service import KafkaService
from app.services.enhanced_kafka_service import EnhancedKafkaService
from app.services.ai_service import AIService
from app.services.dapr_service import DaprService

__all__ = [
    "AuthService",
    "ExerciseService",
    "SubmissionService",
    "ProgressService",
    "ChatService",
    "KafkaService",
    "EnhancedKafkaService",
    "AIService",
    "DaprService",
]
