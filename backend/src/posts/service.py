from typing import Literal, Optional

from src.core.database import Post, reddit_db


def create(
    author_id: int,
    subreddit_id: int,
    title: str,
    content: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> Optional[Post]:
    return reddit_db.create_post(author_id, subreddit_id, title, content, latitude, longitude)


def get_by_id(post_id: int) -> Optional[Post]:
    return reddit_db.get_post(post_id)


def get_user_posts(user_id: int) -> list[Post]:
    return reddit_db.get_user_posts(user_id)


def get_feed(user_id: int, sort: str, limit: int, offset: int = 0) -> list[Post]:
    if sort != reddit_db.get_user_sort(user_id):
        reddit_db.change_feed_sort(user_id, sort)
    return reddit_db.get_feed(user_id, limit, offset)


def get_feed_count(user_id: int) -> int:
    return reddit_db.get_feed_count(user_id)


def get_closest_feed(
    user_id: int,
    limit: int,
    radius_km: Optional[float] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> list[tuple[Post, float]]:
    return reddit_db.get_closest_feed(user_id, limit, radius_km, latitude, longitude)


def vote(post_id: int, user_id: int, direction: Literal["up", "down", "remove"]) -> None:
    if direction == "up":
        reddit_db.upvote_post(post_id, user_id)
    elif direction == "down":
        reddit_db.downvote_post(post_id, user_id)
    else:
        current = reddit_db.get_post_vote(post_id, user_id)
        if current == 1:
            reddit_db.upvote_post(post_id, user_id)
        elif current == -1:
            reddit_db.downvote_post(post_id, user_id)


def get_vote(post_id: int, user_id: int) -> int:
    return reddit_db.get_post_vote(post_id, user_id)


def share(post_id: int, user_id: int) -> bool:
    return reddit_db.share_post(post_id, user_id)
