"""
Определения всех ачивок и условия их получения.
Каждая ачивка — это словарь с кодом, названием и условием.
Условие — это функция, которая принимает статистику пользователя
и возвращает True, если ачивка должна быть выдана.
"""


ACHIEVEMENTS_DATA = [
    {
        "code": "first_anime",
        "title": "Первое аниме",
        "description": "Добавь своё первое аниме в список",
        "xp_reward": 10,
        "icon": "🎬",
    },
    {
        "code": "five_anime",
        "title": "Пятёрка",
        "description": "Добавь 5 аниме в свой список",
        "xp_reward": 20,
        "icon": "📚",
    },
    {
        "code": "ten_anime",
        "title": "Десятка",
        "description": "Добавь 10 аниме в свой список",
        "xp_reward": 30,
        "icon": "📖",
    },
    {
        "code": "first_completed",
        "title": "Первый просмотр",
        "description": "Заверши просмотр первого аниме",
        "xp_reward": 15,
        "icon": "✅",
    },
    {
        "code": "five_completed",
        "title": "Марафонец",
        "description": "Заверши просмотр 5 аниме",
        "xp_reward": 30,
        "icon": "🏃",
    },
    {
        "code": "critic",
        "title": "Критик",
        "description": "Поставь 5 оценок аниме",
        "xp_reward": 25,
        "icon": "⭐",
    },
    {
        "code": "level_2",
        "title": "Зритель",
        "description": "Достигни 2 уровня",
        "xp_reward": 20,
        "icon": "🌱",
    },
    {
        "code": "level_5",
        "title": "Знаток",
        "description": "Достигни 5 уровня",
        "xp_reward": 50,
        "icon": "🎓",
    },
]


def check_first_anime(stats: dict) -> bool:
    """Добавлено первое аниме"""
    return stats.get("total_in_list", 0) >= 1


def check_five_anime(stats: dict) -> bool:
    """Добавлено 5 аниме"""
    return stats.get("total_in_list", 0) >= 5


def check_ten_anime(stats: dict) -> bool:
    """Добавлено 10 аниме"""
    return stats.get("total_in_list", 0) >= 10


def check_first_completed(stats: dict) -> bool:
    """Завершено первое аниме"""
    return stats.get("completed_count", 0) >= 1


def check_five_completed(stats: dict) -> bool:
    """Завершено 5 аниме"""
    return stats.get("completed_count", 0) >= 5


def check_critic(stats: dict) -> bool:
    """Поставлено 5 оценок"""
    return stats.get("scored_count", 0) >= 5


def check_level_2(stats: dict) -> bool:
    """Достигнут 2 уровень"""
    return stats.get("level", 1) >= 2


def check_level_5(stats: dict) -> bool:
    """Достигнут 5 уровень"""
    return stats.get("level", 1) >= 5


ACHIEVEMENT_CHECKS = {
    "first_anime": check_first_anime,
    "five_anime": check_five_anime,
    "ten_anime": check_ten_anime,
    "first_completed": check_first_completed,
    "five_completed": check_five_completed,
    "critic": check_critic,
    "level_2": check_level_2,
    "level_5": check_level_5,
}
