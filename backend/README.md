# GeoThread Backend

FastAPI backend with an in-memory graph-based data store. No database setup required for local development — all data is seeded on startup.

## Requirements

- Python 3.11+
- [Poetry](https://python-poetry.org/) (recommended) or pip

## Running locally

**1. Copy the env file and fill in values**

```bash
cp .env.example .env
```

The only required fields to get the server running are the non-database ones. For local dev with the in-memory store, set the DB fields to anything (they're validated by pydantic-settings but not actually connected to):

```
DB_USER=dev
DB_PASSWORD=dev
DB_HOST=localhost
DB_PORT=5432
DB_NAME=geothread
SECRET_KEY=any-random-string-here
```

**2. Install dependencies**

With Poetry:
```bash
poetry install
poetry shell
```

With pip:
```bash
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**3. Start the server**

```bash
python run.py
```

Or directly with uvicorn:
```bash
uvicorn src.main:app --reload --port 8000
```

The API is available at **http://localhost:8000**. Interactive docs (Swagger UI) are at **http://localhost:8000/docs** (only when `DEBUG=true`).

On startup, `load_dummy_data()` seeds the in-memory store with users, subreddits, posts, comments, and subscriptions — no migration needed.

## Running with Docker

```bash
cp .env.example .env
# fill in .env, then:
docker-compose up --build
```

The app listens on the port set by `APP_HOST_PORT` in `.env` (default `8000`). PostgreSQL is wired automatically inside the compose network.

## Running tests

```bash
pytest
```

## Key env vars

| Variable | Description |
|---|---|
| `SECRET_KEY` | JWT signing key |
| `DEBUG` | Enables `/docs` when `true` |
| `BACKEND_CORS_ORIGINS` | JSON array of allowed frontend origins |
| `LOCATION_DECAY_KM` | Radius used by the location recommendation engine |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT access token lifetime |

## API overview

| Prefix | Description |
|---|---|
| `/api/posts` | Feed, post CRUD, voting, sharing |
| `/api/subreddits` | Communities, subscriptions, recommendations |
| `/api/comments` | Nested comment threads |
| `/api/users` | User profiles |
| `/auth` | Login, register, refresh token |

The feed endpoint (`GET /api/posts`) supports `sort` values: `hot`, `new`, `top`, `rising`, `controversial`, `closest`. The `closest` sort requires either `latitude`/`longitude` query params or a location set on the authenticated user.

## Subreddit online counts

`online_count` on subreddit responses is an estimated active-member count: subscribed users who created a post or a non-deleted comment in that subreddit during the last 24 hours. It is not live websocket presence.
