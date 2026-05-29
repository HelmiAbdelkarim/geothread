# GeoThread Backend

FastAPI backend with a PostgreSQL database and graph-based algorithmic engine. Data persists across restarts via a named Docker volume.

## Quick start (Docker — recommended)

```bash
# 1. Clone
git clone <your-repo-url>
cd geothread

# 2. Start everything (first run builds images — takes ~3 min)
docker-compose up -d --build

# 3. Seed with sample data
docker-compose exec backend python scripts/seed.py

# 4. Open http://localhost:3000
```

That's it. No Python, no Node, no database install needed — Docker handles all of it.

---

**Subsequent starts** (after the first build):

```bash
docker-compose up -d        # data already in DB, no seed needed
```

**After pulling new code:**

```bash
docker-compose build --no-cache   # rebuild images
docker-compose up -d
```

**Full reset** (wipe all data):

```bash
docker-compose down -v      # -v deletes the postgres volume
docker-compose up -d --build
docker-compose exec backend python scripts/seed.py
```

---

## Architecture

The backend is built around custom algorithmic structures required by the ASNAP course project:

| Component | Algorithm | Where |
|---|---|---|
| Feed ranking | Max-heap priority queue with time-decay scoring | `posts/service.py` |
| Comment threads | N-ary tree with DFS traversal | `algorithms/tree.py` |
| Location sorting | Haversine distance formula | `core/database.py` |
| Spatial indexing | Geohash encoding | `core/database.py` |
| Recommendations | Multi-factor scoring (distance + activity + relevance) | `subreddits/service.py` |

Data is stored in PostgreSQL via SQLAlchemy ORM (`core/models.py`). The algorithmic structures operate on data loaded from the DB — combining real persistence with the required in-memory algorithm implementations.

## API overview

| Prefix | Description |
|---|---|
| `/api/posts` | Feed, post CRUD, voting, sharing |
| `/api/subreddits` | Communities, subscriptions, recommendations |
| `/api/comments` | Nested comment threads |
| `/api/users` | User profiles, location |
| `/api/search` | Full-text search across posts, communities, users |
| `/api/auth` | Register, login |

The feed (`GET /api/posts`) works without authentication (returns all posts globally). When authenticated, it returns posts from subscribed subreddits, falling back to global if subscriptions are empty.

Supported `sort` values: `hot`, `new`, `top`, `rising`, `controversial`, `closest`.

## Key env vars

| Variable | Description |
|---|---|
| `DB_HOST` | Postgres host (`db` inside Docker, `localhost` outside) |
| `DEBUG` | Enables `/docs` Swagger UI when `true` |
| `BACKEND_CORS_ORIGINS` | JSON array of allowed frontend origins |
| `LOCATION_DECAY_KM` | Radius used by the location recommendation engine |
| `SECRET_KEY` | JWT signing key |
