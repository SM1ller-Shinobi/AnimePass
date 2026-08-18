from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.models.achievement import Achievement, UserAchievement
from app.api.deps import get_current_user

router = APIRouter(prefix="/me", tags=["achievements"])


@router.get("/achievements")
def get_my_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    achievements = db.query(
        Achievement,
        UserAchievement.unlocked_at
    ).join(
        UserAchievement,
        Achievement.id == UserAchievement.achievement_id
    ).filter(
        UserAchievement.user_id == current_user.id
    ).all()

    return [
        {
            "code": a.code,
            "title": a.title,
            "description": a.description,
            "xp_reward": a.xp_reward,
            "icon": a.icon,
            "unlocked_at": unlocked_at.isoformat() if unlocked_at else None,
        }
        for a, unlocked_at in achievements
    ]


@router.get("/achievements/all")
def get_all_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    all_achievements = db.query(Achievement).all()

    user_achievement_ids = db.query(UserAchievement.achievement_id).filter(
        UserAchievement.user_id == current_user.id
    ).all()
    user_ids = {row[0] for row in user_achievement_ids}

    return [
        {
            "code": a.code,
            "title": a.title,
            "description": a.description,
            "xp_reward": a.xp_reward,
            "icon": a.icon,
            "is_unlocked": a.id in user_ids,
        }
        for a in all_achievements
    ]
