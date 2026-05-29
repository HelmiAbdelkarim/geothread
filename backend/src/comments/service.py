from typing import Dict, List, Literal, Optional

from src.core.database import Comment, reddit_db


def create(author_id: int, post_id: int, content: str, parent_comment_id: Optional[int] = None) -> Optional[Comment]:
    return reddit_db.create_comment(author_id, post_id, content, parent_comment_id)


def get_by_id(comment_id: int) -> Optional[Comment]:
    return reddit_db.get_comment(comment_id)


def edit(comment_id: int, content: str) -> bool:
    return reddit_db.edit_comment(comment_id, content)


def delete(comment_id: int) -> bool:
    return reddit_db.delete_comment(comment_id)


def get_post_thread(post_id: int, sort_by: str = "score") -> List[Dict]:
    return reddit_db.build_comment_thread(post_id, sort_by)


def vote(comment_id: int, user_id: int, direction: Literal["up", "down", "remove"]) -> None:
    if direction == "up":
        reddit_db.upvote_comment(comment_id, user_id)
    elif direction == "down":
        reddit_db.downvote_comment(comment_id, user_id)
    else:
        current = reddit_db.get_comment_vote(comment_id, user_id)
        if current == 1:
            reddit_db.upvote_comment(comment_id, user_id)
        elif current == -1:
            reddit_db.downvote_comment(comment_id, user_id)


def get_vote(comment_id: int, user_id: int) -> int:
    return reddit_db.get_comment_vote(comment_id, user_id)


def get_depth(post_id: int) -> int:
    return reddit_db.get_comment_depth(post_id)


def get_user_comments(user_id: int) -> List[Comment]:
    return reddit_db.get_user_comments(user_id)
