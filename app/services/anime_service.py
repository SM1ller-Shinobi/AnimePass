import httpx
from typing import List, Optional
from fastapi import HTTPException, status

from app.schemas.anime import Anime

JIKAN_BASE_URL = "https://api.jikan.moe/v4"
TIMEOUT = 15.0


async def search_anime(query: str, limit: int = 10) -> List[Anime]:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                f"{JIKAN_BASE_URL}/anime",
                params={"q": query, "limit": limit, "sfw": True}
            )
            response.raise_for_status()
            data = response.json()
            return [Anime(**item) for item in data.get("data", [])]
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Jikan API слишком долго отвечает. Попробуйте чуть позже."
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ошибка внешнего API (статус {e.response.status_code})"
        )


async def get_top_anime(limit: int = 10) -> List[Anime]:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                f"{JIKAN_BASE_URL}/top/anime",
                params={"limit": limit}
            )
            response.raise_for_status()
            data = response.json()
            return [Anime(**item) for item in data.get("data", [])]
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Jikan API слишком долго отвечает. Попробуйте чуть позже."
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ошибка внешнего API (статус {e.response.status_code})"
        )


async def get_anime_by_id(mal_id: int) -> Optional[Anime]:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(f"{JIKAN_BASE_URL}/anime/{mal_id}")
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
            return Anime(**data.get("data", {}))
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Jikan API слишком долго отвечает. Попробуйте чуть позже."
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ошибка внешнего API (статус {e.response.status_code})"
        )
