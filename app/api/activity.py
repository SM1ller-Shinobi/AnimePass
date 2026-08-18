from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.activity import Activity
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/activity", tags=["activity"])


@router.get("/")
def get_my_activity(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    activities = db.query(Activity).filter(
        Activity.user_id == current_user.id
    ).order_by(Activity.created_at.desc()).limit(limit).all()

    return [
        {
            "id": a.id,
            "action_type": a.action_type,
            "description": a.description,
            "mal_id": a.mal_id,
            "anime_title": a.anime_title,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in activities
    ]


@router.get("/feed")
def get_friends_feed(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.models.friendship import Friendship

    friendships = db.query(Friendship).filter(
        Friendship.status == "accepted",
        (Friendship.requester_id == current_user.id) | 
        (Friendship.addressee_id == current_user.id),
    ).all()

    friend_ids = set()
    for f in friendships:
        friend_id = f.addressee_id if f.requester_id == current_user.id else f.requester_id
        friend_ids.add(friend_id)

    if not friend_ids:
        return []

    activities = db.query(Activity).filter(
        Activity.user_id.in_(friend_ids)
    ).order_by(Activity.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": a.id,
            "user_id": a.user_id,
            "action_type": a.action_type,
            "description": a.description,
            "mal_id": a.mal_id,
            "anime_title": a.anime_title,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in activities
    ]
