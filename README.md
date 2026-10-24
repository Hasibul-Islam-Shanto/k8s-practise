# TechBlog

A small full-stack technology blog. Users register, publish articles, browse and
search what others have written, like posts, and view profiles.

- `backend/` — FastAPI, SQLAlchemy, MySQL, Alembic, JWT auth
- `frontend/` — Vue 3, TypeScript, Vite, Tailwind CSS, Pinia, Vue Router

## Requirements

- Python 3.11+
- Node 20+
- A running MySQL server

## Backend setup

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

cp .env.example .env
# Edit .env: set the MySQL password in DATABASE_URL, and set JWT_SECRET to a
# random string of at least 32 characters:
#   python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

`DATABASE_URL` is a URL, so special characters in the password must be
percent-encoded — `@` becomes `%40`, `:` becomes `%3A`, `/` becomes `%2F`. An
unencoded `@` silently makes the rest of the string parse as the hostname.

Create the database, then run the migrations:

```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS tech_blog CHARACTER SET utf8mb4"
.venv/bin/alembic upgrade head
```

Optionally load development data (8 users, 24 posts, tags and likes). Every
seeded account uses the password `password123`:

```bash
.venv/bin/python -m app.seed
```

Run the API:

```bash
.venv/bin/uvicorn app.main:app --reload
```

It listens on `http://localhost:8000`, with interactive docs at `/docs`.

### Tests

The suite runs against in-memory SQLite, so it needs no MySQL server:

```bash
cd backend
.venv/bin/python -m pytest
```

## Frontend setup

```bash
cd frontend
npm install
cp .env.example .env   # VITE_API_URL, defaults to the local API
npm run dev
```

It serves `http://localhost:5173`, which is also the origin the backend allows
through CORS via `FRONTEND_URL`.

## Docker

The same app can run as three containers: MySQL, the FastAPI backend, and the
built frontend served by nginx on port 80.

```bash
cp .env.example .env
# Edit .env: set MYSQL_ROOT_PASSWORD, MYSQL_PASSWORD, and JWT_SECRET.
# JWT_SECRET must be at least 32 characters.
docker compose up --build -d
```

Open the app at `http://localhost`. Interactive API docs stay on the backend
at `http://localhost:8000/docs`. The browser talks only to nginx; `/api/v1`
is proxied to the backend, so `VITE_API_URL` stays `/api/v1`.

If host port 80 is already in use, change the frontend mapping in
`compose.yaml` to `8080:80` and set `FRONTEND_URL=http://localhost:8080`, then
rebuild.

Optionally load the same development data as the local setup (every seeded
account uses the password `password123`). This clears existing rows first:

```bash
docker compose exec backend python -m app.seed
```

Stop the stack, or stop it and delete the database volume:

```bash
docker compose down
docker compose down -v   # removes MySQL data
```

`MYSQL_PASSWORD` is placed into `DATABASE_URL`. If it contains `@`, `:`, or
`/`, percent-encode those characters the same way as in the local backend
setup.

## API

All routes are prefixed with `/api/v1`.

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| POST | `/auth/register` | — | Create an account, returns a token |
| POST | `/auth/login` | — | Log in with email or username |
| GET | `/auth/me` | required | The current user |
| GET | `/posts` | optional | Feed, with `page`, `limit`, `search`, `tag` |
| GET | `/posts/{id}` | optional | One post |
| POST | `/posts` | required | Create a post |
| PUT | `/posts/{id}` | owner | Update a post |
| DELETE | `/posts/{id}` | owner | Delete a post |
| POST | `/posts/{id}/like` | required | Like a post |
| DELETE | `/posts/{id}/like` | required | Remove a like |
| GET | `/users/{username}` | — | Public profile with statistics |
| GET | `/users/{username}/posts` | optional | That user's posts |
| PUT | `/users/me` | required | Update your own profile |

Authentication is optional rather than absent on read endpoints so that a
logged-in reader gets `liked_by_current_user` on each post.

## Where things live

| Concern | Location |
| --- | --- |
| Password hashing, JWTs, auth dependencies | [backend/app/core/security.py](backend/app/core/security.py) |
| Settings and secrets | [backend/app/core/config.py](backend/app/core/config.py) |
| Database models | [backend/app/models/](backend/app/models/) |
| Route definitions | [backend/app/routes/](backend/app/routes/) |
| Post queries and ownership checks | [backend/app/services/post_service.py](backend/app/services/post_service.py) |
| HTTP client and error parsing | [frontend/src/services/api.ts](frontend/src/services/api.ts) |
| Auth state | [frontend/src/stores/auth.ts](frontend/src/stores/auth.ts) |
| Route guards | [frontend/src/router/index.ts](frontend/src/router/index.ts) |
| Design tokens | [frontend/src/assets/main.css](frontend/src/assets/main.css) |

## Notes on a few choices

- Passwords are hashed with `bcrypt` directly rather than through `passlib`,
  because `passlib` 1.7.4 fails against `bcrypt` 5.x.
- JWTs use `PyJWT`. `config.py` rejects a `JWT_SECRET` shorter than 32
  characters, which is the minimum for HS256.
- A single like per user per post is enforced by a unique constraint on
  `likes (user_id, post_id)`, not just by the endpoint.
- Tailwind 4 is configured in CSS. The palette lives in the `@theme` block in
  `src/assets/main.css`; there is no `tailwind.config.js`.
