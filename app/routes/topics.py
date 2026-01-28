"""
Topic endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.models.models import Topic, Level
from app.schemas import TopicCreate, TopicResponse, TopicUpdate, LevelCreate, LevelResponse
from app.routes.auth import get_current_user_payload, get_current_teacher_id

router = APIRouter(prefix="/api/topics", tags=["topics"])
logger = logging.getLogger(__name__)


# ============= Level Endpoints =============

@router.get("/levels", response_model=list[LevelResponse])
async def get_levels(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get all skill levels"""
    try:
        # Check if user is authenticated
        current_user = get_current_user_payload(request)
        current_user_id = current_user.get("user_id")

        if not current_user_id or current_user_id == 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )

        # Query only the fields we need to avoid relationship loading
        levels = db.query(Level.id, Level.name, Level.description, Level.order, Level.created_at).order_by(Level.order).all()

        # Convert to response objects
        level_responses = []
        for level_row in levels:
            level_resp = LevelResponse(
                id=level_row.id,
                name=level_row.name,
                description=level_row.description,
                order=level_row.order,
                created_at=level_row.created_at
            )
            level_responses.append(level_resp)
        return level_responses
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get levels error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch levels"
        )


@router.post("/levels", response_model=LevelResponse, status_code=status.HTTP_201_CREATED)
async def create_level(
    level: LevelCreate,
    current_teacher_id: int = Depends(get_current_teacher_id),
    db: Session = Depends(get_db)
):
    """Create a new skill level (Teachers only)"""
    try:
        db_level = Level(**level.dict())
        db.add(db_level)
        db.commit()
        db.refresh(db_level)
        return db_level
    except Exception as e:
        db.rollback()
        logger.error(f"Create level error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create level"
        )


# ============= Topic Endpoints =============

@router.post("/", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
async def create_topic(
    topic: TopicCreate,
    current_teacher_id: int = Depends(get_current_teacher_id),
    db: Session = Depends(get_db)
):
    """Create a new topic (Teachers only)"""
    try:
        # Verify level exists
        level = db.query(Level).filter(Level.id == topic.level_id).first()
        if not level:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Level not found"
            )

        db_topic = Topic(**topic.dict())
        db.add(db_topic)
        db.commit()
        db.refresh(db_topic)
        return db_topic
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Create topic error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create topic"
        )


@router.get("/", response_model=list[TopicResponse])
async def list_topics(
    request: Request,
    level_id: int = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List topics with optional filtering"""
    try:
        # Check if user is authenticated
        current_user = get_current_user_payload(request)
        current_user_id = current_user.get("user_id")

        if not current_user_id or current_user_id == 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )

        query = db.query(Topic.id, Topic.name, Topic.description, Topic.level_id,
                        Topic.order, Topic.learning_objectives, Topic.resources,
                        Topic.created_at, Topic.updated_at).order_by(Topic.order)

        if level_id:
            query = query.filter(Topic.level_id == level_id)

        topics = query.offset(skip).limit(limit).all()

        # Convert to response objects
        topic_responses = []
        for topic_row in topics:
            topic_resp = TopicResponse(
                id=topic_row.id,
                name=topic_row.name,
                description=topic_row.description,
                level_id=topic_row.level_id,
                order=topic_row.order,
                learning_objectives=topic_row.learning_objectives,
                resources=topic_row.resources,
                created_at=topic_row.created_at,
                updated_at=topic_row.updated_at
            )
            topic_responses.append(topic_resp)
        return topic_responses
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List topics error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch topics"
        )


@router.get("/{topic_id}", response_model=TopicResponse)
async def get_topic(
    request: Request,
    topic_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific topic"""
    try:
        # Check if user is authenticated
        current_user = get_current_user_payload(request)
        current_user_id = current_user.get("user_id")

        if not current_user_id or current_user_id == 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )

        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found"
            )
        return topic
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get topic error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch topic"
        )


@router.put("/{topic_id}", response_model=TopicResponse)
async def update_topic(
    topic_id: int,
    topic_update: TopicUpdate,
    current_teacher_id: int = Depends(get_current_teacher_id),
    db: Session = Depends(get_db)
):
    """Update a topic (Teachers only)"""
    try:
        db_topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not db_topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found"
            )

        update_data = topic_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_topic, key, value)

        db.commit()
        db.refresh(db_topic)
        return db_topic
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Update topic error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update topic"
        )


@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(
    topic_id: int,
    current_teacher_id: int = Depends(get_current_teacher_id),
    db: Session = Depends(get_db)
):
    """Delete a topic (Teachers only)"""
    try:
        db_topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not db_topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found"
            )

        db.delete(db_topic)
        db.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Delete topic error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete topic"
        )
