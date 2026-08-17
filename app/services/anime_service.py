import httpx
from typing import List, Optional
from app.schemas.anime import Anime, AnimeListResponse


JIKAN_BASE_URL = "https://api.jikan.moe/v4"


async def search_anime(query: str, limit: int = 10) -> List[Anime]:
    """
    Поиск аниме по названию.
    Пример: search_anime("naruto")
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{JIKAN_BASE_URL}/anime",
            params={"q": query, "limit": limit, "sfw": True}
        )
        response.raise_for_status()
        data = response.json()
        # Валидируем каждый элемент через Pydantic
        return [Anime(**item) for item in data.get("data", [])]


async def get_top_anime(limit: int = 10) -> List[Anime]:
    """
    Получить топ аниме по рейтингу.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{JIKAN_BASE_URL}/top/anime",
            params={"limit": limit}
        )
        response.raise_for_status()
        data = response.json()
        return [Anime(**item) for item in data.get("data", [])]


async def get_anime_by_id(mal_id: int) -> Optional[Anime]:
    """
    Получить детальную информацию об аниме по ID.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{JIKAN_BASE_URL}/anime/{mal_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        data = response.json()
        return Anime(**data.get("data", {}))
