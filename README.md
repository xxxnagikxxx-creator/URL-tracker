# Live Checker

Live Checker — это сервис на FastAPI с React-фронтендом для мониторинга ссылок. Пользователь входит через Telegram Login Widget, добавляет URL, а фоновый worker проверяет каждую ссылку каждые 10 минут.

## Стек

- Backend: FastAPI, async SQLAlchemy, PostgreSQL, Alembic
- Auth: Telegram Login Widget, JWT cookies, хранение refresh-токенов в Redis
- Worker: ARQ + Redis
- Frontend: React, Vite, TypeScript
- Runtime: Docker Compose

## Сервисы

Docker Compose запускает:

- `db` - PostgreSQL
- `redis` - Redis с паролем
- `migrate` - применяет миграции через `alembic upgrade head`
- `api` - FastAPI на порту `8000`
- `worker` - ARQ worker с задачей по расписанию
- `bot` - Telegram bot polling
- `frontend` - React-приложение Vite на порту `5173`

## Переменные окружения

Создайте `.env` на основе примера:

```bash
cp .env.example .env
```

Основные значения:

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=live_checker

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=redis_pass

JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
SECRET_KEY=change_me_to_a_long_random_secret

TELEGRAM_BOT_TOKEN=your_botfather_token
TELEGRAM_BOT_USERNAME=testivecheckerbot

VITE_API_URL=http://localhost:8000
```

Не коммитьте `.env`. Этот файл уже добавлен в `.gitignore`.

## Запуск через Docker

```bash
docker-compose up --build
```

Открыть:

- Frontend: http://localhost:5173
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/

Сервис `migrate` применяет миграции до старта `api`, `worker` и `bot`.

## Telegram Login Widget

Telegram Login Widget требует домен, настроенный в BotFather.

В BotFather выполните:

```text
/setdomain
```

Выберите своего бота и укажите домен фронтенда.

Для локальной разработки через туннель:

1. Откройте через туннель frontend-порт `5173`.
2. Откройте через туннель backend-порт `8000`.
3. Укажите backend tunnel URL в `.env`:

```env
VITE_API_URL=https://your-backend-tunnel
```

4. Перезапустите frontend:

```bash
docker-compose restart frontend
```

Vite уже разрешает такие tunnel-домены:

- `*.ru.tuna.am`
- `*.ngrok-free.app`
- `*.trycloudflare.com`

Backend CORS разрешает те же tunnel-домены.

## Полезные команды

Запустить миграции вручную:

```bash
docker-compose run --rm migrate
```

Перезапустить только API:

```bash
docker-compose restart api
```

Перезапустить только frontend:

```bash
docker-compose restart frontend
```

Перезапустить только worker:

```bash
docker-compose restart worker
```

Перезапустить только Telegram-бота:

```bash
docker-compose restart bot
```

Остановить контейнеры:

```bash
docker-compose down
```

Удалить volumes PostgreSQL и Redis:

```bash
docker-compose down -v
```

## Обзор API

Auth:

- `POST /auth/telegram` - вход через подписанные данные Telegram
- `GET /auth/get_full_user` - текущий пользователь
- `POST /auth/refresh` - обновление token cookies
- `POST /auth/logout` - удаление cookies и refresh-токена
- `PUT /auth/update_user` - обновление текущего пользователя
- `DELETE /auth/delete_user` - удаление текущего пользователя

Live checker:

- `POST /live_checker/create_link` - добавить ссылку текущему пользователю
- `GET /live_checker/get_links` - список ссылок текущего пользователя
- `GET /live_checker/get_link/{link_id}` - детали ссылки с историей проверок
- `DELETE /live_checker/delete_link/{link_id}` - удалить свою ссылку

## Безопасность

- Telegram auth payload проверяется через HMAC с использованием `TELEGRAM_BOT_TOKEN`.
- Владелец пользователя определяется из JWT cookies, а не из ID в теле запроса.
- Доступ к ссылкам ограничен по `telegram_id`, поэтому пользователь не может читать или удалять чужие ссылки.
- Refresh-токены хранятся в Redis с TTL.
- Cross-origin авторизация использует cookies `SameSite=None; Secure`, поэтому для разработки через frontend/backend tunnel нужен HTTPS.

## Структура проекта

```text
src/
  main.py
  config.py
  database.py
  telegram_auth/
    routers.py
    services.py
    schemas.py
    models.py
    token.py
    redis.py
    utils.py
    exceptions.py
  live_checker/
    routers.py
    services.py
    schemas.py
    models.py
    utils.py
    worker.py
    exceptions.py
  bot/
    bot.py
    notifications.py
    utils.py
frontend/
  src/
    App.tsx
    api.ts
    types.ts
    styles.css
alembic/
  versions/
```
