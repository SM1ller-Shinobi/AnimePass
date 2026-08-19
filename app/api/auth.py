from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_user_by_email,
    get_user_by_username,
)
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
        "/register", response_model=UserResponse,
        status_code=status.HTTP_201_CREATED
    )
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email уже зарегистрирован"
        )
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username уже занят"
        )

    hashed_pwd = hash_password(user_data.password)
    is_admin_user = user_data.email.lower() == settings.ADMIN_EMAIL.lower()
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pwd,
        is_admin=is_admin_user,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
def login(
    user_data: UserLogin, response: Response, db: Session = Depends(get_db)
):
    user = get_user_by_email(db, user_data.email)
    if not user or not verify_password(
        user_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False,
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    response: Response,
    access_token: str = None,
    db: Session = Depends(get_db),
):

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен не предоставлен",
        )
    try:
        from jose import jwt
        payload = jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Неверный токен")
    except Exception:
        raise HTTPException(status_code=401, detail="Неверный токен")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user
