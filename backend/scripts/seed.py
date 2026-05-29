#!/usr/bin/env python3
"""
GeoThread seed script — populates the API with sample data via HTTP.

Usage:
    python scripts/seed.py [--base-url http://localhost:8000]

The backend seeds itself automatically on startup via load_dummy_data().
Use this script when you migrate to a persistent database and need to
populate it with realistic sample data for development / demos.

Default seed accounts (all pre-loaded on startup):
    helmi_dev   / helmi@geo.io    — Paris, sort: hot
    sara_algo   / sara@geo.io     — Paris, sort: new
    pedro_graphs/ pedro@geo.io    — Paris, sort: top
    nour_isep   / nour@geo.io     — Paris, sort: controversial
    alex_cs     / alex@geo.io     — New York, sort: hot
    maya_fullstack / maya@geo.io  — Seattle, sort: rising
"""

import argparse
import json
import sys
import urllib.error
import urllib.request
from typing import Any

DEFAULT_BASE = "http://localhost:8000"


def req(base: str, method: str, path: str, body: dict | None = None, user_id: int | None = None) -> Any:
    url = f"{base}/api{path}"
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if user_id:
        headers["X-User-Id"] = str(user_id)
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code} on {method} {path}: {e.read().decode()}", file=sys.stderr)
        return None


def seed(base: str) -> None:
    print(f"Seeding GeoThread at {base} …\n")

    # ── Users ──────────────────────────────────────────────────────────────
    print("Creating users…")
    users_data = [
        {"username": "helmi_dev",      "email": "helmi@geo.io"},
        {"username": "sara_algo",      "email": "sara@geo.io"},
        {"username": "pedro_graphs",   "email": "pedro@geo.io"},
        {"username": "nour_isep",      "email": "nour@geo.io"},
        {"username": "alex_cs",        "email": "alex@geo.io"},
        {"username": "maya_fullstack", "email": "maya@geo.io"},
    ]
    users = []
    for u in users_data:
        result = req(base, "POST", "/auth/register", u)
        if result:
            print(f"  ✓ {u['username']} (id={result['user_id']})")
            users.append(result)
        else:
            print(f"  ✗ {u['username']} (may already exist)")

    if not users:
        print("\nNo users created. Fetching existing users…")
        users = req(base, "GET", "/users/") or []

    if not users:
        print("ERROR: no users available, aborting.", file=sys.stderr)
        sys.exit(1)

    # ── Locations ──────────────────────────────────────────────────────────
    print("\nSetting user locations…")
    locations = [
        {"latitude": 48.8566, "longitude": 2.3522,   "city": "Paris",    "region": "Île-de-France", "country": "France"},
        {"latitude": 48.8584, "longitude": 2.2945,   "city": "Paris",    "region": "Île-de-France", "country": "France"},
        {"latitude": 48.8534, "longitude": 2.3332,   "city": "Paris",    "region": "Île-de-France", "country": "France"},
        {"latitude": 48.8924, "longitude": 2.2381,   "city": "Paris",    "region": "Île-de-France", "country": "France"},
        {"latitude": 40.7128, "longitude": -74.0060, "city": "New York", "region": "New York",      "country": "USA"},
        {"latitude": 47.6062, "longitude": -122.3321,"city": "Seattle",  "region": "Washington",    "country": "USA"},
    ]
    for user, loc in zip(users, locations):
        req(base, "PUT", "/users/me/location", loc, user["user_id"])
        print(f"  ✓ {user['username']} → {loc['city']}")

    # ── Subreddits ─────────────────────────────────────────────────────────
    print("\nCreating subreddits…")
    subs_data = [
        {"name": "algorithms",   "description": "Graph theory, complexity, raw implementations."},
        {"name": "python",       "description": "Python news, tips and projects."},
        {"name": "webdev",       "description": "Frontend, backend, devops."},
        {"name": "geothread",    "description": "GeoThread project discussion."},
        {"name": "ParisTech",    "description": "Paris software, startups, and engineering meetups."},
        {"name": "programming",  "description": "General programming discussion."},
        {"name": "technology",   "description": "Tech news and trends."},
    ]
    subs = []
    admin = users[0]["user_id"]
    for s in subs_data:
        result = req(base, "POST", "/subreddits/", s, admin)
        if result:
            print(f"  ✓ r/{s['name']} (id={result['subreddit_id']})")
            subs.append(result)

    if not subs:
        subs = req(base, "GET", "/subreddits/") or []

    # ── Subscriptions ──────────────────────────────────────────────────────
    print("\nSubscribing users to communities…")
    for user in users:
        for sub in subs[:4]:
            req(base, "POST", f"/subreddits/{sub['subreddit_id']}/subscribe", user_id=user["user_id"])
    print(f"  ✓ all users subscribed to first 4 communities")

    # ── Posts ──────────────────────────────────────────────────────────────
    print("\nCreating posts…")
    sub_map = {s["name"]: s["subreddit_id"] for s in subs}
    posts_data = [
        (users[0], "algorithms", "Why Dijkstra fails on negative weights",
         "Dijkstra breaks with negative edges because the greedy relaxation assumes finalized distances cannot improve.",
         48.8584, 2.2945),
        (users[1], "python", "I built a Reddit clone backend in pure Python",
         "For my algorithms class I implemented graph traversal, nested comments, feed ranking, and geospatial recommendations.",
         48.8867, 2.3431),
        (users[2], "webdev", "Tailwind v4 is actually great",
         "The new Vite integration is clean, CSS-first config works well.",
         48.8534, 2.3332),
        (users[0], "geothread", "GeoThread ASNAP engine — first working demo",
         "Feed sorting with hot/new/top/rising/controversial is live.",
         48.8574, 2.3578),
        (users[3], "algorithms", "Union-Find vs label propagation for community detection",
         "Union-Find is simpler and near-constant amortized. Label propagation produces richer clusters.",
         48.8924, 2.2381),
        (users[4], "programming", "Recursion vs iteration — when does it actually matter?",
         "Stack overflow is the obvious risk, but the real tradeoff is readability and state ownership.",
         40.7128, -74.0060),
        (users[5], "webdev", "React Server Components finally make sense to me",
         "The useful mental model is two component trees with a serialization boundary.",
         47.6062, -122.3321),
    ]
    for author, sub_name, title, content, lat, lng in posts_data:
        sid = sub_map.get(sub_name)
        if not sid:
            continue
        body = {"subreddit_id": sid, "title": title, "content": content, "latitude": lat, "longitude": lng}
        result = req(base, "POST", "/posts/", body, author["user_id"])
        if result:
            print(f"  ✓ [{sub_name}] {title[:50]}…")

    print("\nSeed complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed GeoThread sample data.")
    parser.add_argument("--base-url", default=DEFAULT_BASE, help="API base URL")
    args = parser.parse_args()
    seed(args.base_url)
