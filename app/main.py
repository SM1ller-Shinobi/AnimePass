import time
from fastapi import FastAPI
from sqlalchemy import text

from app.db.session import engine, SessionLocal, Base
from app.models.user import User
from app.models.user_anime import UserAnime
from app.api.auth import router as auth_router
from app.api.my_list import router as my_list_router
from app.api.anime import router as anime_router


def wait_for_db(max_retries: int = 10, delay: int = 2):
    for attempt in range(max_retries):
        try:
            with SessionLocal() as session:
                session.execute(text("SELECT 1"))
            print("✅ База данных готова!")
            return True
        except Exception:
            print(f"⏳ Попытка {attempt + 1}/{max_retries}. БД недоступна, ждём {delay}с...")
            time.sleep(delay)
    print("Не удалось подключиться к БД.")
    return False


if wait_for_db():
    Base.metadata.create_all(bind=engine)

app = FastAPI(title="AnimePass")

app.include_router(auth_router)
app.include_router(anime_router)
app.include_router(my_list_router)


@app.get("/")
def home():
    return {"message": "AnimePass API работает!"}
