from typing import Optional

from src.core.database import Redditor, reddit_db


def register(username: str, email: str, sort: Optional[str] = "hot") -> Optional[Redditor]:
    if reddit_db.get_user_by_username(username):
        return None
    return reddit_db.create_user(username=username, email=email, sort=sort)


def get_by_username(username: str) -> Optional[Redditor]:
    return reddit_db.get_user_by_username(username)
