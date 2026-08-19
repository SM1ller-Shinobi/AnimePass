from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from datetime import datetime, timedelta, timezone

from app.db.session import get_db
from app.models.user import User
from app.models.user_anime import UserAnime
from app.models.activity import Activity
from app.models.achievement import UserAchievement
from app.api.deps import get_current_admin
from app.core.gamification import get_level_name

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/overview")
def get_overview(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    total_users = db.query(func.count(User.id)).scalar() or 0
    premium_users = db.query(func.count(User.id)).filter(
        User.is_premium == True
    ).scalar() or 0
    admin_users = db.query(func.count(User.id)).filter(
        User.is_admin == True
    ).scalar() or 0

    premium_conversion = round((premium_users / total_users * 100), 2) if total_users > 0 else 0

    total_anime_records = db.query(func.count(UserAnime.id)).scalar() or 0
    unique_anime_count = db.query(func.count(func.distinct(UserAnime.mal_id))).scalar() or 0

    total_activities = db.query(func.count(Activity.id)).scalar() or 0

    total_achievements_granted = db.query(func.count(UserAchievement.id)).scalar() or 0

    avg_level = db.query(func.avg(User.level)).scalar()
    avg_xp = db.query(func.avg(User.xp)).scalar()

    return {
        "users": {
            "total": total_users,
            "premium": premium_users,
            "admins": admin_users,
            "premium_conversion_percent": premium_conversion,
            "average_level": round(avg_level, 2) if avg_level else 0,
            "average_xp": round(avg_xp, 2) if avg_xp else 0,
        },
        "anime": {
            "total_records": total_anime_records,
            "unique_titles": unique_anime_count,
        },
        "activity": {
            "total_events": total_activities,
            "achievements_granted": total_achievements_granted,
        },
    }


@router.get("/users")
def get_users_list(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    users = db.query(User).order_by(User.created_at.desc()).offset(offset).limit(limit).all()

    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "level": u.level,
            "xp": u.xp,
            "is_premium": u.is_premium,
            "is_admin": u.is_admin,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]


@router.get("/anime/top")
def get_top_anime(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    top = db.query(
        UserAnime.mal_id,
        func.count(UserAnime.id).label("count"),
        func.avg(UserAnime.score).label("avg_score"),
    ).group_by(UserAnime.mal_id).order_by(func.count(UserAnime.id).desc()).limit(limit).all()

    return [
        {
            "mal_id": row.mal_id,
            "added_count": row.count,
            "average_score": round(row.avg_score, 2) if row.avg_score else None,
        }
        for row in top
    ]


@router.get("/activity/recent")
def get_recent_activity(
    days: int = Query(7, ge=1, le=90),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    since = datetime.now(timezone.utc) - timedelta(days=days)

    rows = db.query(
        cast(Activity.created_at, Date).label("day"),
        func.count(Activity.id).label("count"),
    ).filter(
        Activity.created_at >= since
    ).group_by(
        cast(Activity.created_at, Date)
    ).order_by(
        cast(Activity.created_at, Date)
    ).all()

    return [
        {
            "date": row.day.isoformat() if row.day else None,
            "events_count": row.count,
        }
        for row in rows
    ]


@router.get("/premium/conversion")
def get_premium_conversion(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    total_users = db.query(func.count(User.id)).scalar() or 0
    active_premium = db.query(func.count(User.id)).filter(
        User.is_premium == True,
        User.premium_expires_at > datetime.now(timezone.utc),
    ).scalar() or 0

    expired_premium = db.query(func.count(User.id)).filter(
        User.is_premium == False,
        User.premium_expires_at.isnot(None),
    ).scalar() or 0

    never_premium = total_users - active_premium - expired_premium

    return {
        "total_users": total_users,
        "active_premium": active_premium,
        "expired_premium": expired_premium,
        "never_premium": never_premium,
        "conversion_percent": round((active_premium / total_users * 100), 2) if total_users > 0 else 0,
    }


@router.get("/levels/distribution")
def get_level_distribution(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    rows = db.query(
        User.level,
        func.count(User.id).label("count"),
    ).group_by(User.level).order_by(User.level).all()

    return [
        {
            "level": row.level,
            "level_name": get_level_name(row.level),
            "users_count": row.count,
        }
        for row in rows
    ]
