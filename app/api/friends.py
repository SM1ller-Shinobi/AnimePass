from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.friendship import Friendship
from app.api.deps import get_current_user
from app.core.gamification import get_level_name

router = APIRouter(prefix="/friends", tags=["friends"])


@router.post("/request/{user_id}")
def send_friend_request(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user_id == current_user.id:
        raise HTTPException(
            status_code=400, detail="Нельзя добавить себя в друзья"
        )

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    existing = db.query(Friendship).filter(
        Friendship.requester_id == current_user.id,
        Friendship.addressee_id == user_id,
    ).first()

    if existing:
        if existing.status == "accepted":
            raise HTTPException(status_code=400, detail="Вы уже друзья")
        elif existing.status == "pending":
            raise HTTPException(status_code=400, detail="Заявка уже отправлена")
        elif existing.status == "rejected":
            existing.status = "pending"
            db.commit()
            return {"message": "Заявка отправлена повторно"}

    reverse = db.query(Friendship).filter(
        Friendship.requester_id == user_id,
        Friendship.addressee_id == current_user.id,
    ).first()

    if reverse and reverse.status == "pending":
        reverse.status = "accepted"
        db.commit()
        return {"message": f"Теперь вы друзья с {target_user.username}!"}

    friendship = Friendship(
        requester_id=current_user.id,
        addressee_id=user_id,
        status="pending",
    )
    db.add(friendship)
    db.commit()

    return {"message":
            f"Заявка в друзья отправлена пользователю {target_user.username}"}


@router.post("/accept/{user_id}")
def accept_friend_request(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    friendship = db.query(Friendship).filter(
        Friendship.requester_id == user_id,
        Friendship.addressee_id == current_user.id,
        Friendship.status == "pending",
    ).first()

    if not friendship:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    friendship.status = "accepted"
    db.commit()

    requester = db.query(User).filter(User.id == user_id).first()
    return {"message": f"Теперь вы друзья с {requester.username}!"}


@router.post("/reject/{user_id}")
def reject_friend_request(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    friendship = db.query(Friendship).filter(
        Friendship.requester_id == user_id,
        Friendship.addressee_id == current_user.id,
        Friendship.status == "pending",
    ).first()

    if not friendship:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    friendship.status = "rejected"
    db.commit()

    return {"message": "Заявка отклонена"}


@router.get("/")
def get_my_friends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    friendships = db.query(Friendship).filter(
        Friendship.status == "accepted",
        (Friendship.requester_id == current_user.id) | 
        (Friendship.addressee_id == current_user.id),
    ).all()

    friends = []
    for f in friendships:
        friend_id = f.addressee_id if f.requester_id == current_user.id else f.requester_id
        friend = db.query(User).filter(User.id == friend_id).first()
        if friend:
            friends.append({
                "id": friend.id,
                "username": friend.username,
                "avatar_url": friend.avatar_url,
                "level": friend.level,
                "level_name": get_level_name(friend.level),
            })

    return friends


@router.get("/requests")
def get_friend_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    requests = db.query(Friendship).filter(
        Friendship.addressee_id == current_user.id,
        Friendship.status == "pending",
    ).all()

    result = []
    for r in requests:
        requester = db.query(User).filter(User.id == r.requester_id).first()
        if requester:
            result.append({
                "id": requester.id,
                "username": requester.username,
                "avatar_url": requester.avatar_url,
                "level": requester.level,
                "sent_at": r.created_at.isoformat() if r.created_at else None,
            })

    return result
