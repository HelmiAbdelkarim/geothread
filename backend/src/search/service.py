from typing import List

from sqlalchemy.orm import Session

from src.core.models import PostModel, SubredditModel, UserModel


def search_posts(db: Session, query: str, limit: int) -> List[PostModel]:
    pattern = f"%{query}%"
    return db.query(PostModel).filter(
        PostModel.title.ilike(pattern) | PostModel.content.ilike(pattern)
    ).limit(limit).all()


def search_subreddits(db: Session, query: str, limit: int) -> List[SubredditModel]:
    pattern = f"%{query}%"
    return db.query(SubredditModel).filter(
        SubredditModel.name.ilike(pattern) | SubredditModel.description.ilike(pattern)
    ).limit(limit).all()


def search_users(db: Session, query: str, limit: int) -> List[UserModel]:
    return db.query(UserModel).filter(UserModel.username.ilike(f"%{query}%")).limit(limit).all()
