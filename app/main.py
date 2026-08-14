import time
from fastapi import FastAPI
from sqlalchemy import text
from app.db.session import engine, SessionLocal, Base
from app.models.user import User


def wait_for_db(max_retries: int = 10, delay: int = 2):
    """Поднятие БД"""
    for attempt in range(max_retries):
        try:
            with SessionLocal() as session:
                session.execute(text("SELECT 1"))
            print("База данных готова.")
            return True
        except Exception:
            print(f"{attempt + 1}. БД недоступна, ждём {delay}с.")
            time.sleep(delay)
    print("Не удалось подключиться к БД.")
    return False


if wait_for_db():
    Base.metadata.create_all(bind=engine)
else:
    print("Пропускаем создание таблиц — БД недоступна")

app = FastAPI(title="AnimePass")

@app.get("/")
def home():
    return {"message": "AnimePass запускается! 🎌"}
