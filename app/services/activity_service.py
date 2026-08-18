from sqlalchemy.orm import Session
from app.models.activity import Activity


def log_activity(
    db: Session,
    user_id: int,
    action_type: str,
    description: str,
    mal_id: int | None = None,
    anime_title: str | None = None,
):
    activity = Activity(
        user_id=user_id,
        action_type=action_type,
        description=description,
        mal_id=mal_id,
        anime_title=anime_title,
    )
    db.add(activity)
