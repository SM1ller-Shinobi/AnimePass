from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.models.user import User
from app.models.user_anime import UserAnime
from app.schemas.user import UserStatsResponse
from app.api.deps import get_current_user
from app.core.gamification import calculate_level, get_level_name
from app.core.gamification import get_next_level_threshold

router = APIRouter(prefix="/me", tags=["stats"])

@router.get("/stats", response_model=UserStatsResponse)
def get_my_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Статистика пользователя: уровень, XP, количество аниме по статусам"""

    stats = db.query(
        UserAnime.status,
        func.count(UserAnime.id)
    ).filter(
        UserAnime.user_id == current_user.id
    ).group_by(UserAnime.status).all()

    status_counts = {status: count for status, count in stats}

    completed_count = status_counts.get("completed", 0)
    watching_count = status_counts.get("watching", 0)
    plan_to_watch_count = status_counts.get("plan_to_watch", 0)
    dropped_count = status_counts.get("dropped", 0)
    total_in_list = sum(status_counts.values())

    level = calculate_level(completed_count)
    level_name = get_level_name(level)
    next_threshold = get_next_level_threshold(level)

    if current_user.level != level:
        current_user.level = level
        db.commit()
        db.refresh(current_user)

    return UserStatsResponse(
        level=level,
        level_name=level_name,
        xp=current_user.xp,
        completed_count=completed_count,
        watching_count=watching_count,
        plan_to_watch_count=plan_to_watch_count,
        dropped_count=dropped_count,
        total_in_list=total_in_list,
        next_level_threshold=next_threshold,
    )
