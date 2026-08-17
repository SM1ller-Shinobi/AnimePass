from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.services.anime_service import search_anime
from app.services.anime_service import get_top_anime, get_anime_by_id
from app.schemas.anime import Anime


router = APIRouter(prefix="/anime", tags=["anime"])


@router.get("/search", response_model=List[Anime])
async def search(
    q: str = Query(
        ..., min_length=1, max_length=100, description="Название аниме"
    ),
    limit: int = Query(10, ge=1, le=25, description="Количество результатов"),
):
    """Поиск аниме по названию"""
    results = await search_anime(q, limit)
    return results


@router.get("/top", response_model=List[Anime])
async def top(
    limit: int = Query(10, ge=1, le=25, description="Количество результатов"),
):
    """Топ аниме по рейтингу"""
    results = await get_top_anime(limit)
    return results


@router.get("/{mal_id}", response_model=Anime)
async def anime_details(mal_id: int):
    """Детальная информация об аниме"""
    anime = await get_anime_by_id(mal_id)
    if anime is None:
        raise HTTPException(status_code=404, detail="Аниме не найдено")
    return anime
