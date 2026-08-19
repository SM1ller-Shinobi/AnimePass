import sys
import os
import random
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine, Base
from app.models.user import User
from app.models.user_anime import UserAnime
from app.models.activity import Activity
from app.models.achievement import Achievement, UserAchievement
from app.models.ad import AdCampaign
from app.core.security import hash_password
from app.core.gamification import calculate_level
from app.services.gamification_service import seed_achievements
from app.services.ad_service import seed_ads


# Реальные mal_id популярных аниме (из Jikan API)
ANIME_MAL_IDS = [
    1,      # Cowboy Bebop
    5,      # Cowboy Bebop: Tengoku no Tobira
    6,      # Trigun
    20,     # Naruto
    21,     # One Piece
    30,     # Shinseiki Evangelion
    33,     # Kenpuu Denki Berserk
    47,     # Akira
    164,    # Mononoke Hime
    170,    # Naruto: Shippuuden
    173,    # Dragon Ball Z
    199,    # Sen to Chihiro no Kamikakushi
    235,    # Gankutsuou
    245,    # Great Teacher Onizuka
    257,    # Fullmetal Alchemist
    512,    # Death Note
    9253,   # Steins;Gate
    11061,  # Hunter x Hunter (2011)
    15335,  # Gintama Movie 2
    17325,  # Attack on Titan
    19815,  # No Game No Life
    22535,  # Kiseijuu: Sei no Kakuritsu
    28977,  # Gintama°
    30276,  # One Punch Man
    32281,  # Kimi no Na wa.
    34599,  # Made in Abyss
    35839,  # Sora yori mo Tooi Basho
    36838,  # Mob Psycho 100 II
    37956,  # Vinland Saga
    38000,  # Kimetsu no Yaiba
    39535,  # Mushoku Tensei
    40748,  # Jujutsu Kaisen
    41467,  # Bleach: Sennen Kessen-hen
    42963,  # Chainsaw Man
    45649,  # Spy x Family
    48556,  # Frieren: Beyond Journey's End
]

USERNAMES = [
    "anime_fan", "otaku_king", "sakura_chan", "naruto_lover", "onepiece_pro",
    "attack_titan", "demon_slayer", "jujutsu_sorcerer", "spy_family_fan",
    "chainsaw_devil", "mob_psycho", "steins_gate", "death_note_user",
    "gintama_lover", "hunter_x_hunter", "berserk_fan", "evangelion_pilot",
    "ghoul_tokyo", "fullmetal_alchemist", "code_geass", "light_yagami",
    "l_detective", "ryuk_apple", "edward_elric", "goku_saiyan", "luffy_pirate",
    "zoro_swordsman", "sanji_cook", "nami_navigator", "usopp_sniper",
    "chopper_doctor", "robin_archaeologist", "frank cyborg", "brook_musician",
    "jinbe_fishman", "shanks_red_hair", "ace_fire", "sabo_revolutionary",
    "dragon_monkey", "garp_hero", "sengoku_buddha", "akainu_admiral",
    "aokiji_admiral", "kizaru_admiral", "fujitora_admiral", "ryokugyu_admiral",
    "mihawk_hawk", "buggy_clown", "crocodile_sir", "doflamingo_joker",
    "kaido_dragon", "big_mom", "blackbeard_teach", "whitebeard_edward",
]

EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "mail.ru", "yandex.ru"]

STATUSES = ["watching", "completed", "plan_to_watch", "dropped", "on_hold"]
STATUS_WEIGHTS = [0.2, 0.4, 0.2, 0.1, 0.1]  # Вероятности каждого статуса


def clear_all_data(db: Session):
    print("Очищаю базу данных...")
    db.query(UserAchievement).delete()
    db.query(UserAnime).delete()
    db.query(Activity).delete()
    db.query(User).delete()
    db.commit()
    print("База очищена")


def generate_users(db: Session, count: int) -> list:
    print(f"Создаю {count} пользователей...")
    users = []

    for i in range(count):
        username = f"{random.choice(USERNAMES)}_{random.randint(100, 999)}"
        email = f"{username}@{random.choice(EMAIL_DOMAINS)}"
        password = "password123"  # Все тестовые пользователи имеют одинаковый пароль

        user = User(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            is_premium=False,
            is_active=True,
            is_admin=False,
            level=1,
            xp=0,
            created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 365)),
        )
        db.add(user)
        users.append(user)

    db.commit()

    for user in users:
        db.refresh(user)

    print(f"Создано {len(users)} пользователей")
    return users


def generate_user_anime(db: Session, users: list):
    print("Генерирую списки аниме...")

    for user in users:
        num_anime = random.randint(5, 30)
        selected_anime = random.sample(ANIME_MAL_IDS, min(num_anime, len(ANIME_MAL_IDS)))

        for mal_id in selected_anime:
            status = random.choices(STATUSES, weights=STATUS_WEIGHTS, k=1)[0]

            score = None
            if status in ["completed", "watching"] and random.random() > 0.3:
                score = random.randint(6, 10)  # Большинство оценок высокие

            episodes_watched = 0
            if status == "completed":
                episodes_watched = random.choice([12, 13, 24, 25, 26, 50, 100, 150, 200, 500])
            elif status == "watching":
                episodes_watched = random.randint(1, 20)
            elif status == "on_hold":
                episodes_watched = random.randint(1, 10)

            user_anime = UserAnime(
                user_id=user.id,
                mal_id=mal_id,
                status=status,
                score=score,
                episodes_watched=episodes_watched,
                added_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 180)),
            )
            db.add(user_anime)

    db.commit()
    print("Списки аниме созданы")


def update_user_levels(db: Session, users: list):
    print("Обновляю уровни и XP...")

    for user in users:
        completed_count = db.query(UserAnime).filter(
            UserAnime.user_id == user.id,
            UserAnime.status == "completed"
        ).count()

        user.level = calculate_level(completed_count)
        user.xp = completed_count * 20 + random.randint(0, 100)  # Примерный XP

    db.commit()
    print("Уровни обновлены")


def generate_activities(db: Session, users: list):
    print("Генерирую активность...")

    action_types = [
        ("added_anime", "Добавил аниме в список"),
        ("completed_anime", "Завершил просмотр аниме"),
        ("got_achievement", "Получил ачивку"),
        ("level_up", "Повысил уровень"),
    ]

    for user in users:
        # От 10 до 50 записей активности
        num_activities = random.randint(10, 50)

        for _ in range(num_activities):
            action_type, description = random.choice(action_types)
            mal_id = random.choice(ANIME_MAL_IDS) if random.random() > 0.3 else None

            activity = Activity(
                user_id=user.id,
                action_type=action_type,
                description=description,
                mal_id=mal_id,
                created_at=datetime.now(timezone.utc) - timedelta(
                    days=random.randint(0, 90),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59),
                ),
            )
            db.add(activity)

    db.commit()
    print("Активность создана")


def assign_premium_users(db: Session, users: list, percentage: float = 0.2):
    num_premium = int(len(users) * percentage)
    premium_users = random.sample(users, num_premium)

    print(f"Назначаю премиум {num_premium} пользователям...")

    for user in premium_users:
        user.is_premium = True
        user.premium_expires_at = datetime.now(timezone.utc) + timedelta(days=random.randint(10, 60))

    db.commit()
    print(f"Назначено {num_premium} премиум-пользователей")


def assign_admin_users(db: Session, users: list, admin_emails: list):
    if not admin_emails:
        return

    print(f"Назначаю админов: {admin_emails}")

    for email in admin_emails:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.is_admin = True
            print(f"  {email} теперь админ")
        else:
            print(f"  Пользователь {email} не найден")

    db.commit()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Seed script for AnimePass")
    parser.add_argument("--clear", action="store_true", help="Clear all data before seeding")
    parser.add_argument("--users", type=int, default=50, help="Number of users to create")
    parser.add_argument("--premium-percent", type=float, default=0.2, help="Percentage of premium users")
    parser.add_argument("--admin-emails", nargs="*", default=[], help="Emails to make admin")

    args = parser.parse_args()

    print("Запуск seed-скрипта...")

    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        seed_achievements(db)
        seed_ads(db)

        if args.clear:
            clear_all_data(db)

        users = generate_users(db, args.users)
        generate_user_anime(db, users)
        update_user_levels(db, users)
        generate_activities(db, users)
        assign_premium_users(db, users, args.premium_percent)

        if args.admin_emails:
            assign_admin_users(db, users, args.admin_emails)

    print("=" * 50)
    print("Seed завершён успешно!")
    print(f"Создано: {args.users} пользователей")
    print(f"Премиум: {int(args.users * args.premium_percent)} пользователей")
    print(f"Пароль для всех тестовых пользователей: password123")


if __name__ == "__main__":
    main()
