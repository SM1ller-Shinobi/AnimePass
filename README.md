# AnimePass

> **Трекер аниме с геймификацией, социальными функциями и премиум-подпиской**

AnimePass — это веб-сервис для фанатов аниме, где можно вести списки просмотренного аниме, ставить оценки, получать достижения, прокачивать профиль. Базовые функции бесплатны с рекламой, премиум открывает расширенные возможности.



## Стек технологий



**Backend** | FastAPI, SQLAlchemy 2.0, Pydantic v2
**Database** | PostgreSQL 16 
**Authentication** | JWT (python-jose), bcrypt (passlib)
**External API** | Jikan API (MyAnimeList) 
**Containerization** | Docker, docker-compose 
**Language** | Python 3.11+ 



## Функционал

### Аутентификация
Регистрация с валидацией email и пароля (минимум 8 символов, буквы + цифры)
JWT-токены в httpOnly cookies для безопасности
Хеширование паролей через bcrypt
Автоматическое продление токенов

### Контент аниме
Поиск аниме через Jikan API (MyAnimeList)
Топ аниме по рейтингу
Детальная информация: жанры, оценки, статусы
Обработка ошибок внешнего API (таймауты, 5xx)

### Списки пользователя
Статусы: `watching`, `completed`, `plan_to_watch`, `dropped`, `on_hold`
Оценки от 1 до 10
Трекинг просмотренных эпизодов
Upsert-логика: обновление существующей записи или создание новой

### Геймификация
**10 уровней** от «Новичок» до «Бог аниме»
**XP за действия**: добавление (+5), завершение (+20), оценка (+5)
**Система ачивок**: Первое аниме, Критик, Марафонец, Знаток и др.
Автоматическая проверка и выдача ачивок после каждого действия

### Социальные функции
**Друзья**: отправка, принятие и отклонение заявок
Автоматическое принятие встречной заявки
**Публичные профили** с уровнями и статистикой
**Лента активности**: свои действия и лента друзей

### Премиум-подписка
Симуляция оплаты (в будущем — интеграция с другими сервисами)
Подписка на 30 дней с датой окончания
Отключение рекламы для премиум-пользователей
Расширенная статистика (средняя оценка, топ аниме, эпизоды)

### Админ-дашборд
Общие метрики платформы (пользователи, конверсия, активность)
Топ аниме по добавлениям
Активность по дням
Конверсия в премиум
Распределение пользователей по уровням
Защита через RBAC (role-based access control)



## Быстрый старт

### Требования
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Python 3.11 или выше
- Git

### Установка

**1. Клонируйте репозиторий:**
```bash
git clone https://github.com/SM1ller-Shinobi/AnimePass.git
cd animepass
```

**2. Создайте виртуальное окружение:**
```bash
python -m venv venv
source venv\Scripts\activate
```

**3. Установите зависимости:**
```bash
pip install -r requirements.txt
```

**4. Настройте переменные окружения:**
Создайте файл .env в корне проекта и скопируйте в него:

DATABASE_URL=postgresql+psycopg2://animepass:animepass_secret@localhost:5432/animepass_db
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
ADMIN_EMAIL=admin@example.com

**5. Запустите базу данных:**
```bash
docker compose up -d
```

**6. Запустите сервер:**
```bash
uvicorn app.main:app --reload
```

**7. Откройте документацию API:**
Перейдите в браузере по ссылке http://127.0.0.1:8000/docs, можно тестировать все эндпоинты

## Наполнение тестовыми данными

Для наполнения базы данными (50 пользователей, списки аниме, активность):
```bash
# Базовый запуск (50 пользователей)
python scripts/seed_data.py

# С очисткой базы и 100 пользователями
python scripts/seed_data.py --clear --users 100

# С админскими email
python scripts/seed_data.py --clear --users 50 --admin-emails admin@example.com
```

## API эндпоинты

**Auth:**
/auth/register (POST) - Регистрация нового пользователя
/auth/login (POST) - Логин, получение JWT-токена
/auth/me (GET) - Текущий авторизованный пользователь

**Anime:**
/anime/search?q=naruto (GET) - Поиск аниме
/anime/top?limit=10 (GET) - Топ аниме по рейтингу
/anime/{mal_id} (GET) - Детальная информация об аниме

**My list:**
/me/anime/ (POST) - Добавить/обновить аниме в списке
/me/anime/?status_filter=completed (GET) - Получить свой список
/me/anime/{mal_id} (DELETE) - Удалить из списка

**Stats:**
/me/stats (GET) - Общая статистика пользователя
/me/stats/premium (GET) - Расширенная статистика (premium)

**Achievements:**
/me/achievements (GET) - Мои полученные ачивки
/me/achievements/all (GET) - Все ачивки с пометкой о получении

**Friends:**
/friends/request/{user_id} (POST) - Отправить заявку в друзья
/friends/accept/{user_id} (POST) - Принять заявку
/friends/reject/{user_id} (POST) - Отклонить заявку
/friends/ (GET) - Мои друзья
/friends/requests (GET) - Входящие заявки

**Users:**
/users/{username} (GET) - Публичный профиль пользователя
/users/search?q=john (GET) - Поиск пользователя

**Activity:**
/activity/ (GET) - Моя лента активности
/activity/feed (GET) - Лента активности друзей

**Premium:**
/me/premium/subscribe (POST) - Купить премиум (симуляция)
/me/premium/cancel (POST) - Отменить подписку
/me/premium/status (GET) - Статус подписки

**Ads:**
/ads/current (GET) - текущая реклама (null для premium)

**Admin:**
/admin/overview (GET) - Общие метрики платформы
/admin/users (GET) - Список пользователей
/admin/anime/top (GET) - Топ аниме по добавлениям
/admin/activity/recent?days=7 (GET) - Активность по дням
/admin/premium/conversion (GET) - Коверсия в премиум
/admin/levels/distribution (GET) - Распределение по уровням

## Переменные окружения
DATABASE_URL - Строка подключения к PostgreSQL
SECRET_KEY - Секретный ключ для JWT
ADMIN_EMAIL - Email администратора (по умолч. admin@example.com)
ALGORITHM - Алгорит хеширования JWT (по умолч. HS256)
ACCESS_TOKEN_EXPIRE_MINUTES - Время жизни токена (по умолч. 10080 - 7 дней)

## Проект будет дорабатываться

## Автор
SM1ller / Александр Миллер

GitHub: https://github.com/SM1ller-Shinobi
Telegram: @SM1ller
