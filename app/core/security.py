"""
Security utilities - Super simple authentication without tokens or hashing
"""

from typing import Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

def hash_password(password: str) -> str:
    """Super simple password - just return as-is for development"""
    return password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Super simple password verification - direct comparison"""
    return plain_password == hashed_password
