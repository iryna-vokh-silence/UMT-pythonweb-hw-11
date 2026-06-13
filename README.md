# Contacts API

REST API для управління контактами з аутентифікацією користувачів.

## Технології

- **FastAPI** — веб-фреймворк
- **PostgreSQL** — база даних
- **SQLAlchemy** — ORM
- **JWT** (python-jose) — авторизація
- **bcrypt** — хешування паролів
- **fastapi-mail** — відправка email
- **Cloudinary** — зберігання аватарів
- **slowapi** — rate limiting
- **Docker Compose** — оркестрація сервісів

## Запуск

### 1. Налаштування змінних середовища

Скопіюй `.env.example` у `.env` та заповни значення:

```bash
cp .env.example .env
```

Обов'язкові поля:

| Змінна | Опис |
|---|---|
| `DATABASE_URL` | URL підключення до PostgreSQL |
| `SECRET_KEY` | Секретний ключ для JWT |
| `MAIL_USERNAME` | SMTP логін (напр. Mailtrap) |
| `MAIL_PASSWORD` | SMTP пароль |
| `MAIL_SERVER` | SMTP сервер |
| `CLOUDINARY_NAME` | Cloudinary cloud name |
| `CLOUDINARY_API_KEY` | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret |

### 2. Запуск через Docker Compose

```bash
docker compose up --build
```

API буде доступне на `http://localhost:8000`

### 3. Запуск локально (без Docker)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

> Потрібен запущений PostgreSQL. `DATABASE_URL` в `.env` має вказувати на `localhost`.

## Документація API

Після запуску: [http://localhost:8000/docs](http://localhost:8000/docs)

## Ендпоінти

### Аутентифікація

| Метод | URL | Опис |
|---|---|---|
| `POST` | `/auth/signup` | Реєстрація нового користувача |
| `POST` | `/auth/login` | Отримання JWT токена |
| `GET` | `/auth/verify/{token}` | Верифікація email |

### Користувач

| Метод | URL | Опис |
|---|---|---|
| `GET` | `/users/me` | Дані поточного користувача (ліміт 10 запитів/хв) |
| `PATCH` | `/users/avatar` | Оновлення аватара (Cloudinary) |

### Контакти (потребують авторизації)

| Метод | URL | Опис |
|---|---|---|
| `POST` | `/contacts/` | Створення контакту |
| `GET` | `/contacts/` | Список контактів (фільтри: `name`, `last_name`, `email`) |
| `GET` | `/contacts/birthdays` | Контакти з днями народження в наступні 7 днів |
| `GET` | `/contacts/{id}` | Отримання контакту за ID |
| `PUT` | `/contacts/{id}` | Оновлення контакту |
| `DELETE` | `/contacts/{id}` | Видалення контакту |

## Особливості

- Кожен користувач має доступ лише до своїх контактів
- Паролі зберігаються виключно у хешованому вигляді (bcrypt)
- Email верифікація через JWT токен (діє 24 години)
- CORS увімкнено для всіх джерел
- Rate limiting на `/users/me`: 10 запитів на хвилину
