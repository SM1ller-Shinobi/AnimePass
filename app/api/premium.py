from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/me/premium", tags=["premium"])

PREMIUM_DURATION_DAYS = 30


@router.post("/subscribe")
def subscribe_to_premium(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.is_premium_active:
        raise HTTPException(
            status_code=400,
            detail="У вас уже есть активная премиум-подписка"
        )

    current_user.is_premium = True
    current_user.premium_expires_at = datetime.now(timezone.utc) + timedelta(days=PREMIUM_DURATION_DAYS)
    db.commit()
    db.refresh(current_user)

    return {
        "message": "Премиум-подписка активирована!",
        "is_premium": True,
        "expires_at": current_user.premium_expires_at.isoformat(),
    }


@router.post("/cancel")
def cancel_premium(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.is_premium_active:
        raise HTTPException(
            status_code=400,
            detail="У вас нет активной премиум-подписки"
        )

    current_user.is_premium = False
    db.commit()
    db.refresh(current_user)

    return {
        "message": "Премиум-подписка отменена",
        "is_premium": False,
    }


@router.get("/status")
def get_premium_status(
    current_user: User = Depends(get_current_user),
):
    is_active = current_user.is_premium_active

    return {
        "is_premium": is_active,
        "expires_at": current_user.premium_expires_at.isoformat() if current_user.premium_expires_at else None,
        "benefits": [
            "Отключение рекламы",
            "Расширенная статистика",
            "Создание коллекций",
            "Кастомизация профиля",
        ] if not is_active else [
            "Реклама отключена ✅",
            "Расширенная статистика ✅",
            "Создание коллекций ✅",
            "Кастомизация профиля ✅",
        ],
    }
