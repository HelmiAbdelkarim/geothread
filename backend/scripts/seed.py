#!/usr/bin/env python3
"""
GeoThread seed script — populates the API with Paris-local sample data.

Usage:
    python scripts/seed.py [--base-url http://localhost:8000]

Runs inside the backend container:
    docker-compose exec backend python scripts/seed.py

Default seed accounts (pre-loaded on startup):
    helmi_dev       / helmi@geo.io    — Issy-les-Moulineaux
    sara_algo       / sara@geo.io     — 15ème arrondissement
    pedro_graphs    / pedro@geo.io    — Ivry-sur-Seine
    nour_isep       / nour@geo.io     — La Défense
    alex_cs         / alex@geo.io     — New York
    maya_fullstack  / maya@geo.io     — Seattle
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
        body_text = e.read().decode()
        print(f"  HTTP {e.code} on {method} {path}: {body_text}", file=sys.stderr)
        return None


def vote(base: str, post_id: int, user_id: int, direction: str = "up") -> None:
    req(base, "POST", f"/posts/{post_id}/vote", {"direction": direction}, user_id)


def comment(base: str, post_id: int, user_id: int, content: str, parent_id: int | None = None) -> Any:
    return req(base, "POST", "/comments/", {
        "post_id": post_id,
        "content": content,
        "parent_comment_id": parent_id,
    }, user_id)


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

    # Build a name→user map
    user_by_name = {u["username"]: u for u in users}

    # ── Locations (specific Paris neighbourhoods) ─────────────────────────
    print("\nSetting user locations…")
    locations = {
        "helmi_dev":      {"latitude": 48.8228, "longitude": 2.2712,   "city": "Issy-les-Moulineaux", "region": "Île-de-France", "country": "France"},
        "sara_algo":      {"latitude": 48.8472, "longitude": 2.2930,   "city": "Paris 15ème",         "region": "Île-de-France", "country": "France"},
        "pedro_graphs":   {"latitude": 48.8113, "longitude": 2.3828,   "city": "Ivry-sur-Seine",      "region": "Île-de-France", "country": "France"},
        "nour_isep":      {"latitude": 48.8924, "longitude": 2.2381,   "city": "Paris La Défense",    "region": "Île-de-France", "country": "France"},
        "alex_cs":        {"latitude": 40.7128, "longitude": -74.0060, "city": "New York",            "region": "New York",      "country": "USA"},
        "maya_fullstack": {"latitude": 47.6062, "longitude": -122.3321,"city": "Seattle",             "region": "Washington",    "country": "USA"},
    }
    for user in users:
        name = user["username"]
        if name in locations:
            req(base, "PUT", "/users/me/location", locations[name], user["user_id"])
            print(f"  ✓ {name} → {locations[name]['city']}")

    # ── Subreddits ─────────────────────────────────────────────────────────
    print("\nCreating subreddits…")
    subs_data = [
        {"name": "algorithms",  "description": "Graph theory, complexity, raw implementations."},
        {"name": "python",      "description": "Python news, tips and projects."},
        {"name": "webdev",      "description": "Frontend, backend, devops."},
        {"name": "geothread",   "description": "GeoThread project discussion."},
        {"name": "ParisTech",   "description": "Paris software, startups, and engineering meetups."},
        {"name": "programming", "description": "General programming discussion."},
        {"name": "technology",  "description": "Tech news and trends."},
        {"name": "Paris",       "description": "Paris community — actus, bons plans, et vie locale."},
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

    sub_map = {s["name"]: s["subreddit_id"] for s in subs}

    # ── Subscriptions ──────────────────────────────────────────────────────
    print("\nSubscribing users…")
    paris_users = [u for u in users if u["username"] in ("helmi_dev", "sara_algo", "pedro_graphs", "nour_isep")]
    for user in users:
        for name in ("geothread",):
            sid = sub_map.get(name)
            if sid:
                req(base, "POST", f"/subreddits/{sid}/subscribe", user_id=user["user_id"])
    for user in paris_users:
        for name in ("Paris", "ParisTech"):
            sid = sub_map.get(name)
            if sid:
                req(base, "POST", f"/subreddits/{sid}/subscribe", user_id=user["user_id"])
    print("  ✓ done")

    # ── Posts (Paris-local only) ───────────────────────────────────────────
    print("\nCreating posts…")

    helmi  = user_by_name.get("helmi_dev")
    sara   = user_by_name.get("sara_algo")
    pedro  = user_by_name.get("pedro_graphs")
    nour   = user_by_name.get("nour_isep")

    # (author, subreddit_name, title, content, lat, lng, location_name)
    posts_data = [
        (helmi,  "Paris",
         "Marché des Puces de Saint-Ouen — guide pour les geeks",
         "Trois allées tech au marché de Saint-Ouen : vintage, rétro-gaming et composants. Plan et horaires 2025.",
         48.9010, 2.3440, "Saint-Ouen"),

        (sara,   "ParisTech",
         "Station F lance un programme IA pour les startups IdF",
         "Nouveau programme Station F focalisé IA générative + hardware. 6 mois, 30 startups sélectionnées.",
         48.8313, 2.3700, "13ème arrondissement"),

        (pedro,  "Paris",
         "Ivry-sur-Seine — FabLab ouvert au public le week-end",
         "Le FabLab d'Ivry ouvre ses portes samedi et dimanche. Laser, imprimantes 3D, électronique. Inscription libre.",
         48.8113, 2.3828, "Ivry-sur-Seine"),

        (nour,   "ParisTech",
         "Apéro tech La Défense — jeudi prochain 18h30",
         "Apéro informel La Défense Tech chaque jeudi. Networking décontracté, 30-50 personnes, tous profils bienvenus.",
         48.8924, 2.2381, "La Défense"),

        (helmi,  "Paris",
         "Nouveau tiers-lieu à Issy — ouverture en septembre",
         "Un tiers-lieu de 800m² ouvre à Issy-les-Moulineaux en septembre. Co-working, ateliers, et espace événements.",
         48.8228, 2.2712, "Issy-les-Moulineaux"),

        (sara,   "ParisTech",
         "Formation MLOps gratuite — ISEP en partenariat avec Scaleway",
         "Cycle de 4 ateliers MLOps gratuits co-organisé ISEP × Scaleway. Inscription via le site ISEP.",
         48.8547, 2.3414, "15ème arrondissement"),

        (pedro,  "Paris",
         "Boulogne-Billancourt — startup weekend 48h ce mois-ci",
         "Startup Weekend Boulogne : 48h pour pitcher, former une équipe et prototyper. Ouvert à tous niveaux.",
         48.8352, 2.2399, "Boulogne-Billancourt"),

        (nour,   "ParisTech",
         "Conférence graph algorithms — Sorbonne, mardi 14h",
         "Conférence sur les algorithmes de graphes appliqués aux réseaux sociaux. Entrée libre sur inscription.",
         48.8494, 2.3429, "5ème arrondissement"),

        (helmi,  "Paris",
         "Vincennes — nouveau café coworking ouvert près du château",
         "Café coworking 'Le Donjon' ouvert à Vincennes : WiFi fibre, prises partout, calme garanti.",
         48.8483, 2.4392, "Vincennes"),

        (sara,   "Paris",
         "Montrouge — quartier tech discret mais actif au sud",
         "Montrouge concentre une dizaine de scale-ups discrètes. Loyers bas, accès RER B, bonne ambiance.",
         48.8183, 2.3197, "Montrouge"),
    ]

    created_posts = []
    for author, sub_name, title, content, lat, lng, loc_name in posts_data:
        if not author:
            continue
        sid = sub_map.get(sub_name)
        if not sid:
            continue
        body = {
            "subreddit_id": sid,
            "title": title,
            "content": content,
            "latitude": lat,
            "longitude": lng,
            "location_name": loc_name,
        }
        result = req(base, "POST", "/posts/", body, author["user_id"])
        if result:
            print(f"  ✓ [{sub_name}] {title[:55]}…")
            created_posts.append((result, author))

    # ── Votes ──────────────────────────────────────────────────────────────
    print("\nAdding votes to all posts in feed…")
    # Collect all post IDs visible in each Paris user's feed
    all_post_ids: set[int] = set()
    for user in paris_users:
        feed = req(base, "GET", f"/posts/?sort=new&limit=100", user_id=user["user_id"]) or []
        for p in feed:
            all_post_ids.add(p["post_id"])

    voted = 0
    for pid in all_post_ids:
        for user in paris_users:
            vote(base, pid, user["user_id"], "up")
            voted += 1
        # A few downvotes for realism
        for user in [u for u in users if u["username"] in ("alex_cs", "maya_fullstack")]:
            vote(base, pid, user["user_id"], "down")
            voted += 1
    print(f"  ✓ {voted} votes cast across {len(all_post_ids)} posts")

    # ── Comments ───────────────────────────────────────────────────────────
    print("\nAdding comments to seed posts…")
    comments_added = 0

    def add_comment(post_id, author, text, parent_id=None):
        nonlocal comments_added
        result = comment(base, post_id, author["user_id"], text, parent_id)
        if result:
            comments_added += 1
        return result

    for (post, author) in created_posts:
        pid = post["post_id"]
        sub = post.get("subreddit_name", "")

        if "Saint-Ouen" in (post.get("location_name") or ""):
            c1 = add_comment(pid, sara,  "L'allée 7 a les meilleurs composants vintage. Arriver avant 10h.")
            add_comment(pid, pedro, "Merci ! Je cherchais justement un clavier mécanique d'époque.", c1["comment_id"] if c1 else None)
            add_comment(pid, nour,  "Ils acceptent la carte bancaire ou c'est cash uniquement ?")

        elif "Station F" in post.get("title", ""):
            c1 = add_comment(pid, pedro, "J'ai postulé. Le dossier est exigeant mais le programme en vaut la peine.")
            add_comment(pid, helmi, "Est-ce qu'il faut déjà avoir un MVP ou juste une idée ?", c1["comment_id"] if c1 else None)
            add_comment(pid, pedro, "Un MVP fonctionnel est fortement recommandé selon le FAQ.", c1["comment_id"] if c1 else None)

        elif "FabLab" in post.get("title", ""):
            c1 = add_comment(pid, sara,  "Je suis allée samedi dernier. Super équipement, équipe sympa.")
            add_comment(pid, helmi, "Il faut une formation préalable pour le laser cutter ?", c1["comment_id"] if c1 else None)
            add_comment(pid, sara,  "Oui, 30 minutes de prise en main obligatoire. Ça se fait sur place.", c1["comment_id"] if c1 else None)

        elif "Apéro tech" in post.get("title", ""):
            add_comment(pid, helmi, "Je viens jeudi ! C'est à quelle adresse exactement ?")
            add_comment(pid, sara,  "Pareil. Dress code ou tenue décontractée ?")
            add_comment(pid, nour,  "Tenue libre, c'est très informel. Rendez-vous côté Grande Arche.")

        elif "tiers-lieu" in post.get("title", "") or "Issy" in (post.get("location_name") or ""):
            c1 = add_comment(pid, sara,  "Super nouvelle pour Issy. Est-ce que ça inclut des espaces dédiés aux développeurs ?")
            add_comment(pid, helmi, "Oui, une salle machines avec stations Linux est prévue.", c1["comment_id"] if c1 else None)

        elif "MLOps" in post.get("title", ""):
            c1 = add_comment(pid, pedro, "Scaleway a une bonne réputation côté infra cloud EU. Beau partenariat.")
            add_comment(pid, nour,  "Il reste des places ? Le lien d'inscription est mort.", c1["comment_id"] if c1 else None)

        elif "startup weekend" in post.get("title", "").lower():
            add_comment(pid, sara,  "Je forme une équipe autour d'un projet éducatif. Qui est partant ?")
            add_comment(pid, helmi, "Je suis intéressé côté backend Python. Ping en DM.")

        elif "graph algorithms" in post.get("title", "").lower() or "Sorbonne" in post.get("content", ""):
            add_comment(pid, helmi, "Je mets ça dans mon agenda. Le speaker est connu dans la communauté ?")
            add_comment(pid, pedro, "Oui, c'est le labo MLIA de Sorbonne. Excellents travaux sur les GNN.")

        elif "Vincennes" in (post.get("location_name") or ""):
            c1 = add_comment(pid, nour,  "Enfin un endroit calme à Vincennes ! Le bruit des cafés habituels est insupportable.")
            add_comment(pid, sara,  "Ils ont des abonnements ou uniquement à la journée ?", c1["comment_id"] if c1 else None)
            add_comment(pid, helmi, "Abonnements mensuels à 80€. Petits-dèj inclus le mardi.", c1["comment_id"] if c1 else None)

        elif "Montrouge" in (post.get("location_name") or ""):
            add_comment(pid, pedro, "RER B en 10 min depuis Châtelet. Vraiment pratique depuis la rive gauche.")
            add_comment(pid, nour,  "Les loyers bureau sont à combien au m² là-bas ?")

    print(f"  ✓ {comments_added} comments added")
    print("\nSeed complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed GeoThread Paris-local data.")
    parser.add_argument("--base-url", default=DEFAULT_BASE, help="API base URL")
    args = parser.parse_args()
    seed(args.base_url)
