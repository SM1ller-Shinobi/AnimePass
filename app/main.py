import time
from fastapi import FastAPI
from sqlalchemy import text

from app.db.session import engine, SessionLocal, Base
from app.models.user import User
from app.models.user_anime import UserAnime
from app.models.friendship import Friendship
from app.models.activity import Activity
from app.models.ad import AdCampaign
from app.services.gamification_service import seed_achievements
from app.services.ad_service import seed_ads
from app.api.auth import router as auth_router
from app.api.my_list import router as my_list_router
from app.api.anime import router as anime_router
from app.api.stats import router as stats_router
from app.api.achievements import router as achievements_router
from app.api.users import router as users_router
from app.api.friends import router as friends_router
from app.api.activity import router as activity_router
from app.api.premium import router as premium_router
from app.api.ads import router as ads_router
from app.api.admin import router as admin_router


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

if wait_for_db():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed_achievements(session)
        seed_ads(session)

app = FastAPI(title="AnimePass")

app.include_router(auth_router)
app.include_router(anime_router)
app.include_router(my_list_router)
app.include_router(stats_router)
app.include_router(achievements_router)
app.include_router(users_router)
app.include_router(friends_router)
app.include_router(activity_router)
app.include_router(premium_router)
app.include_router(ads_router)
app.include_router(admin_router)


@app.get("/")
def home():
    return {"message": "AnimePass API работает!"}
