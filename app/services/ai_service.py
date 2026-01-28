"""
AI Service for generating agent responses using Gemini
"""

import logging
from typing import List, Dict, Any
import openai
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIService:
    """Service for interacting with Gemini AI"""
    
    # Mock responses for development when API key is not available
    MOCK_RESPONSES = {
        "general": [
            "I'm here to help! What would you like to learn about?",
            "That's a great question! Based on what you're studying, you might want to focus on understanding the core concepts first.",
            "I see. Let me help you break this down into smaller parts to make it easier to understand.",
            "Good thinking! Have you tried practicing with some examples to reinforce this concept?"
        ],
        "concepts": [
            "This concept is fundamental to programming. Think of it like...",
            "Let me explain this step by step so it makes sense.",
            "This is similar to something you might see in real-world programming.",
            "The key insight here is understanding how these parts work together."
        ],
        "debug": [
            "I see what might be happening. Can you tell me what output you're getting?",
            "Let's trace through your code step by step. What's the first thing that happens?",
            "Here's a hint: check what the value of this variable is at this point.",
            "Try running this part of your code separately to isolate the problem."
        ],
        "exercise": [
            "Great effort! Let's work through this together. What part are you stuck on?",
            "You're on the right track! Let me guide you through the next step.",
            "Think about what this step should do. What do you expect to happen?",
            "Good! Now try applying the same logic to solve the rest of the problem."
        ]
    }
    
    @staticmethod
    def _get_client():
        """Get OpenAI-compatible client for Gemini"""
        return openai.OpenAI(
            api_key=settings.gemini_api_key,
            base_url=settings.gemini_base_url
        )

    @classmethod
    async def generate_response(cls, messages: List[Dict[str, str]], agent_type: str = "general") -> str:
        """Generate a response from Gemini based on chat history"""
        if not settings.gemini_api_key:
            logger.warning("Gemini API key not configured. Using mock responses for development.")
            # Return a mock response from the appropriate agent type
            import random
            responses = cls.MOCK_RESPONSES.get(agent_type, cls.MOCK_RESPONSES["general"])
            return random.choice(responses)

        try:
            client = cls._get_client()
            
            # Add system prompt based on agent type
            system_prompts = {
                "general": "You are a helpful educational assistant on the LearnFlow platform. Assist students with their learning queries.",
                "concepts": "You are a subject matter expert. Explain complex concepts in simple terms for students.",
                "debug": "You are a coding mentor. Help students debug their code by providing guidance and hints rather than direct solutions.",
                "exercise": "You are a tutor. Help students work through their exercises step-by-step."
            }
            
            system_role = system_prompts.get(agent_type, system_prompts["general"])
            
            full_messages = [{"role": "system", "content": system_role}] + messages
            
            response = client.chat.completions.create(
                model=settings.gemini_model,
                messages=full_messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return "I encountered an error while thinking. Let's try again in a moment."

