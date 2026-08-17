from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.models.user_anime import UserAnime
from app.schemas.user_anime import UserAnimeCreate, UserAnimeResponse
from app.api.deps import get_current_user
from app.models.user import User

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
    """Добавить аниме в список или обновить статус/оценку"""

    db_anime = db.query(UserAnime).filter(
        UserAnime.user_id == current_user.id,
        UserAnime.mal_id == anime_data.mal_id
    ).first()

    if db_anime:
        db_anime.status = anime_data.status
        db_anime.score = anime_data.score
        db_anime.episodes_watched = anime_data.episodes_watched
    else:
        db_anime = UserAnime(
            user_id=current_user.id,
            mal_id=anime_data.mal_id,
            status=anime_data.status,
            score=anime_data.score,
            episodes_watched=anime_data.episodes_watched,
        )
        db.add(db_anime)

    db.commit()
    db.refresh(db_anime)
    return db_anime


@router.get("/", response_model=List[UserAnimeResponse])
def get_my_list(
    status_filter: Optional[str] = Query(
        None, description="Фильтр по статусу"
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить свой список аниме"""
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
    """Удалить аниме из своего списка"""
    db_anime = db.query(UserAnime).filter(
        UserAnime.user_id == current_user.id,
        UserAnime.mal_id == mal_id
    ).first()

    if not db_anime:
        raise HTTPException(
            status_code=404, detail="Аниме не найдено в вашем списке"
        )

    db.delete(db_anime)
    db.commit()
    return None
