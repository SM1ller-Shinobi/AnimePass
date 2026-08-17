from typing import Optional, List
from pydantic import BaseModel


class AnimeImage(BaseModel):
    image_url: str


class Images(BaseModel):
    jpg: AnimeImage


class Trailer(BaseModel):
    youtube_id: Optional[str] = None
    url: Optional[str] = None
    embed_url: Optional[str] = None


class Genre(BaseModel):
    mal_id: int
    name: str


class Anime(BaseModel):
    mal_id: int
    title: str
    title_english: Optional[str] = None
    title_japanese: Optional[str] = None
    images: Images
    trailer: Optional[Trailer] = None
    synopsis: Optional[str] = None
    episodes: Optional[int] = None
    status: Optional[str] = None
    score: Optional[float] = None
    scored_by: Optional[int] = None
    rank: Optional[int] = None
    popularity: Optional[int] = None
    members: Optional[int] = None
    genres: List[Genre] = []
    year: Optional[int] = None


class AnimeListResponse(BaseModel):
    data: List[Anime]
