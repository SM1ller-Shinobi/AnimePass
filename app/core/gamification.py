"""
Модуль геймификации: уровни, XP, награды.
"""

# Пороги уровней: индекс = уровень - 1, значение = количество completed аниме
LEVEL_THRESHOLDS = [
    0,    # Уровень 1: 0 аниме (старт)
    2,    # Уровень 2: 2 аниме
    5,    # Уровень 3: 5 аниме
    10,   # Уровень 4: 10 аниме
    20,   # Уровень 5: 20 аниме
    40,   # Уровень 6: 40 аниме
    80,   # Уровень 7: 80 аниме
    150,  # Уровень 8: 150 аниме
    250,  # Уровень 9: 250 аниме
    500,  # Уровень 10: 500 аниме
]

LEVEL_NAMES = [
    "Новичок",      # 1
    "Зритель",      # 2
    "Любитель",     # 3
    "Поклонник",    # 4
    "Знаток",       # 5
    "Эксперт",      # 6
    "Мастер",       # 7
    "Сенсей",       # 8
    "Легенда",      # 9
    "Бог аниме",    # 10
]

# XP за действия
XP_REWARDS = {
    "add_to_list": 5,       # Добавил аниме в список
    "set_score": 5,         # Поставил оценку
    "complete_anime": 20,   # Завершил просмотр
    "update_progress": 1,   # Обновил количество эпизодов
}

def calculate_level(completed_count: int) -> int:
    """
    Рассчитывает уровень на основе количества просмотренных аниме.

    Args:
        completed_count: количество аниме со статусом 'completed'

    Returns:
        Уровень от 1 до 10
    """
    level = 1
    for i, threshold in enumerate(LEVEL_THRESHOLDS):
        if completed_count >= threshold:
            level = i + 1
        else:
            break
    return level


def get_level_name(level: int) -> str:
    """Возвращает название уровня"""
    if 1 <= level <= len(LEVEL_NAMES):
        return LEVEL_NAMES[level - 1]
    return "Неизвестный"


def get_next_level_threshold(level: int) -> int | None:
    """
    Возвращает количество аниме, необходимое для следующего уровня.
    Если максимальный уровень — возвращает None.
    """
    if level >= len(LEVEL_THRESHOLDS):
        return None
    return LEVEL_THRESHOLDS[level]


def get_xp_for_action(action: str) -> int:
    """Возвращает XP за действие"""
    return XP_REWARDS.get(action, 0)
