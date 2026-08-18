from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.db.session import get_db
from app.models.user import User
from app.models.user_anime import UserAnime
from app.core.gamification import get_level_name

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/search")
def search_users(
    q: str = Query(..., min_length=1, max_length=50),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    users = db.query(User).filter(
        or_(
            User.username.ilike(f"%{q}%"),
            User.email.ilike(f"%{q}%"),
        ),
        User.is_active == True,
    ).limit(limit).all()

    return [
        {
            "id": u.id,
            "username": u.username,
            "avatar_url": u.avatar_url,
            "level": u.level,
            "level_name": get_level_name(u.level),
            "xp": u.xp,
        }
        for u in users
    ]


@router.get("/{username}")
def get_user_profile(
    username: str,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    stats = db.query(
        UserAnime.status,
        func.count(UserAnime.id)
    ).filter(
        UserAnime.user_id == user.id
    ).group_by(UserAnime.status).all()

    status_counts = {status: count for status, count in stats}

    return {
        "id": user.id,
        "username": user.username,
        "avatar_url": user.avatar_url,
        "bio": user.bio,
        "level": user.level,
        "level_name": get_level_name(user.level),
        "xp": user.xp,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "anime_stats": {
            "completed": status_counts.get("completed", 0),
            "watching": status_counts.get("watching", 0),
            "plan_to_watch": status_counts.get("plan_to_watch", 0),
            "dropped": status_counts.get("dropped", 0),
            "total": sum(status_counts.values()),
        },
    }
