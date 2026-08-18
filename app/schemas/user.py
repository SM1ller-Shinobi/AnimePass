import re
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if len(v) < 3 or len(v) > 50:
            raise ValueError("Username должен быть от 3 до 50 символов")
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError(
                "Username может содержать только английские буквы, цифры и _"
            )
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Пароль должен быть минимум 8 символов")
        if not re.search(r"[a-zA-Z]", v):
            raise ValueError("Пароль должен содержать хотя бы одну букву")
        if not re.search(r"\d", v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_premium: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserStatsResponse(BaseModel):
    level: int
    level_name: str
    xp: int
    completed_count: int
    watching_count: int
    plan_to_watch_count: int
    dropped_count: int
    total_in_list: int
    next_level_threshold: int | None

    class Config:
        from_attributes = True

