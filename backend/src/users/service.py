from typing import Optional

from src.core.database import Location, Redditor, reddit_db


def get_by_id(user_id: int) -> Optional[Redditor]:
    return reddit_db.get_user(user_id)


def get_by_username(username: str) -> Optional[Redditor]:
    return reddit_db.get_user_by_username(username)


def list_all() -> list[Redditor]:
    return reddit_db.users.get_all()


def get_stats(user_id: int) -> Optional[dict]:
    return reddit_db.get_user_stats(user_id)


def update_location(user_id: int, location: Location) -> bool:
    return reddit_db.update_user_location(user_id, location)
