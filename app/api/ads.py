from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.ad import AdCampaign
from app.api.deps import get_current_user

router = APIRouter(prefix="/ads", tags=["ads"])


@router.get("/current")
def get_current_ad(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.is_premium_active:
        return {"show_ad": False, "ad": None}

    ad = db.query(AdCampaign).filter(
        AdCampaign.is_active == True
    ).first()

    if not ad:
        return {"show_ad": False, "ad": None}

    return {
        "show_ad": True,
        "ad": {
            "id": ad.id,
            "title": ad.title,
            "content": ad.content,
            "image_url": ad.image_url,
            "link_url": ad.link_url,
        },
    }
