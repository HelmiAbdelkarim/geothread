from src.core.database import Post, Redditor, Subreddit, reddit_db


def search_posts(query: str, limit: int) -> list[Post]:
    return reddit_db.search_posts(query, limit)


def search_subreddits(query: str, limit: int) -> list[Subreddit]:
    return reddit_db.search_subreddits(query, limit)


def search_users(query: str, limit: int) -> list[Redditor]:
    return reddit_db.search_users(query, limit)

