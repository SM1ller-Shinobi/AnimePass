from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.db.session import get_db
from app.models.user_anime import UserAnime
from app.schemas.user_anime import UserAnimeCreate, UserAnimeResponse
from app.api.deps import get_current_user
from app.models.user import User
from app.core.gamification import calculate_level
from app.services.gamification_service import grant_xp, check_and_grant_achievements
from app.services.activity_service import log_activity

router = APIRouter(prefix="/me/anime", tags=["my_list"])


@router.post(
        "/", response_model=UserAnimeResponse,
        status_code=status.HTTP_201_CREATED
    )
def add_or_update_anime(
    anime_data: UserAnimeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    db_anime = db.query(UserAnime).filter(
        UserAnime.user_id == current_user.id,
        UserAnime.mal_id == anime_data.mal_id
    ).first()

    is_new = db_anime is None
    xp_gained = 0
    old_status = None
    old_score = None

    if db_anime:
        old_status = db_anime.status
        old_score = db_anime.score

        db_anime.status = anime_data.status
        db_anime.score = anime_data.score
        db_anime.episodes_watched = anime_data.episodes_watched

        if anime_data.status == "completed" and old_status != "completed":
            xp_gained += grant_xp(db, current_user, "complete_anime")
        if anime_data.score and not old_score:
            xp_gained += grant_xp(db, current_user, "set_score")
        if anime_data.episodes_watched > 0:
            xp_gained += grant_xp(db, current_user, "update_progress")
    else:
        db_anime = UserAnime(
            user_id=current_user.id,
            mal_id=anime_data.mal_id,
            status=anime_data.status,
            score=anime_data.score,
            episodes_watched=anime_data.episodes_watched,
        )
        db.add(db_anime)
        xp_gained += grant_xp(db, current_user, "add_to_list")

        if anime_data.status == "completed":
            xp_gained += grant_xp(db, current_user, "complete_anime")
        if anime_data.score:
            xp_gained += grant_xp(db, current_user, "set_score")

    db.commit()
    db.refresh(db_anime)

    completed_count = db.query(func.count(UserAnime.id)).filter(
        UserAnime.user_id == current_user.id,
        UserAnime.status == "completed"
    ).scalar() or 0
    new_level = calculate_level(completed_count)
    if current_user.level != new_level:
        current_user.level = new_level
        db.commit()

    if is_new:
        log_activity(
            db,
            user_id=current_user.id,
            action_type="added_anime",
            description=f"Добавил аниме (mal_id={anime_data.mal_id}) в список",
            mal_id=anime_data.mal_id,
        )

    if anime_data.status == "completed" and old_status != "completed":
        log_activity(
            db,
            user_id=current_user.id,
            action_type="completed_anime",
            description=f"Завершил просмотр аниме (mal_id={anime_data.mal_id})",
            mal_id=anime_data.mal_id,
        )

    granted_achievements = check_and_grant_achievements(db, current_user)

    db.commit()

    if xp_gained > 0:
        print(f"🎮 Пользователь {current_user.username} получил {xp_gained} XP")
    if granted_achievements:
        print(f"🏆 Пользователь {current_user.username} получил ачивки: {granted_achievements}")

    return db_anime


@router.get("/", response_model=List[UserAnimeResponse])
def get_my_list(
    status_filter: Optional[str] = Query(
        None, description="Фильтр по статусу"
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(UserAnime).filter(UserAnime.user_id == current_user.id)

    if status_filter:
        query = query.filter(UserAnime.status == status_filter)

    return query.order_by(UserAnime.updated_at.desc()).all()


@router.delete("/{mal_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_list(
    mal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_anime = db.query(UserAnime).filter(
        UserAnime.user_id == current_user.id,
        UserAnime.mal_id == mal_id
    ).first()

    if not db_anime:
        raise HTTPException(
            status_code=404,
            detail="Аниме не найдено в вашем списке"
        )

    db.delete(db_anime)
    db.commit()
    return None
