from typing import List, Optional

from src.core.database import Post, SubredditRecommendation, Subreddit, reddit_db


def create(name: str, description: str, topic: Optional[str] = None) -> Subreddit:
    return reddit_db.create_subreddit(name, description, topic=topic)


def get_by_id(subreddit_id: int) -> Optional[Subreddit]:
    return reddit_db.get_subreddit(subreddit_id)


def get_by_name(name: str) -> Optional[Subreddit]:
    return reddit_db.get_subreddit_by_name(name)


def list_all() -> List[Subreddit]:
    return reddit_db.get_all_subreddits()


def get_posts(subreddit_id: int) -> List[Post]:
    return reddit_db.get_subreddit_posts(subreddit_id)


def get_online_count(subreddit_id: int) -> int:
    return reddit_db.get_online_count(subreddit_id)


def subscribe(user_id: int, subreddit_id: int) -> bool:
    return reddit_db.subscribe(user_id, subreddit_id)


def unsubscribe(user_id: int, subreddit_id: int) -> bool:
    return reddit_db.unsubscribe(user_id, subreddit_id)


def get_recommendations(user_id: int, limit: int = 10) -> List[SubredditRecommendation]:
    return reddit_db.get_recommendations(user_id, limit)
