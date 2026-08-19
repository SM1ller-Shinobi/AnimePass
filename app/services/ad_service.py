from sqlalchemy.orm import Session
from app.models.ad import AdCampaign


def seed_ads(db: Session):
    """Заполняет таблицу рекламы тестовыми данными."""
    existing_count = db.query(AdCampaign).count()
    if existing_count > 0:
        return

    ads = [
        AdCampaign(
            title="AnimePass Premium",
            content="Отключи рекламу и получи расширенную статистику всего за 299₽/мес!",
            image_url=None,
            link_url="/premium",
            is_active=True,
        ),
        AdCampaign(
            title="Фигурки аниме персонажей",
            content="Огромный выбор фигурок с доставкой по всему миру. Скидка 20% по промокоду ANIME20!",
            image_url=None,
            link_url="https://example.com/figures",
            is_active=True,
        ),
    ]

    for ad in ads:
        db.add(ad)
    db.commit()
