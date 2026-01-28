"""
Initialize routes module
"""

from app.routes.auth import router as auth_router
from app.routes.exercises import router as exercises_router
from app.routes.submissions import router as submissions_router
from app.routes.progress import router as progress_router
from app.routes.chat import router as chat_router
from app.routes.analytics import router as analytics_router
from app.routes.topics import router as topics_router
from app.routes.quizzes import router as quizzes_router
from app.routes.teacher_dashboard import router as teacher_dashboard_router

__all__ = [
    "auth_router",
    "exercises_router",
    "submissions_router",
    "progress_router",
    "chat_router",
    "analytics_router",
    "topics_router",
    "quizzes_router",
    "teacher_dashboard_router",
]
