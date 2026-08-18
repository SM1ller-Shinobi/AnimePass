from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import User
from app.models.user_anime import UserAnime
from app.models.achievement import Achievement, UserAchievement
from app.core.gamification import XP_REWARDS, calculate_level
from app.core.achievements import ACHIEVEMENTS_DATA, ACHIEVEMENT_CHECKS
from app.services.activity_service import log_activity


def seed_achievements(db: Session):
    existing_count = db.query(Achievement).count()
    if existing_count > 0:
        return

    for data in ACHIEVEMENTS_DATA:
        achievement = Achievement(
            code=data["code"],
            title=data["title"],
            description=data["description"],
            xp_reward=data["xp_reward"],
            icon=data.get("icon"),
        )
        db.add(achievement)
    db.commit()


def grant_xp(db: Session, user: User, action: str) -> int:
    xp = XP_REWARDS.get(action, 0)
    if xp > 0:
        user.xp += xp
    return xp


def get_user_stats_for_achievements(db: Session, user: User) -> dict:
    total_in_list = db.query(func.count(UserAnime.id)).filter(
        UserAnime.user_id == user.id
    ).scalar() or 0

    completed_count = db.query(func.count(UserAnime.id)).filter(
        UserAnime.user_id == user.id,
        UserAnime.status == "completed"
    ).scalar() or 0

    scored_count = db.query(func.count(UserAnime.id)).filter(
        UserAnime.user_id == user.id,
        UserAnime.score.isnot(None)
    ).scalar() or 0

    level = calculate_level(completed_count)

    return {
        "total_in_list": total_in_list,
        "completed_count": completed_count,
        "scored_count": scored_count,
        "level": level,
    }


def check_and_grant_achievements(db: Session, user: User) -> list:
    stats = get_user_stats_for_achievements(db, user)
    granted = []

    existing_achievements = db.query(UserAchievement.achievement_id).filter(
        UserAchievement.user_id == user.id
    ).all()
    existing_ids = {row[0] for row in existing_achievements}

    for code, check_func in ACHIEVEMENT_CHECKS.items():
        # Проверяем условие
        if not check_func(stats):
            continue

        achievement = db.query(Achievement).filter(
            Achievement.code == code
        ).first()

        if not achievement:
            continue

        if achievement.id in existing_ids:
            continue

        user_achievement = UserAchievement(
            user_id=user.id,
            achievement_id=achievement.id,
        )
        db.add(user_achievement)
        user.xp += achievement.xp_reward
        granted.append(achievement.title)

        log_activity(
            db,
            user_id=user.id,
            action_type="got_achievement",
            description=f"Получил ачивку «{achievement.title}» {achievement.icon or ''}",
        )

    return granted
