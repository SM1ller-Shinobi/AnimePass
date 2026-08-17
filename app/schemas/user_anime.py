from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class UserAnimeCreate(BaseModel):
    mal_id: int
    status: str = "plan_to_watch"
    score: Optional[int] = None
    episodes_watched: int = 0

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = [
            "watching", "completed", "plan_to_watch", "dropped", "on_hold"
        ]
        if v not in allowed:
            raise ValueError(f"Статус должен быть одним из: {allowed}")
        return v

    @field_validator("score")
    @classmethod
    def validate_score(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and (v < 1 or v > 10):
            raise ValueError("Оценка должна быть от 1 до 10")
        return v


class UserAnimeResponse(UserAnimeCreate):
    id: int
    user_id: int
    added_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
