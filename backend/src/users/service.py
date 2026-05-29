from typing import List, Optional

from sqlalchemy.orm import Session

from src.core.database import Location, geohash_encode
from src.core.models import PostModel, SubscriptionModel, UserModel


def get_by_id(db: Session, user_id: int) -> Optional[UserModel]:
    return db.query(UserModel).filter(UserModel.user_id == user_id).first()


def get_by_username(db: Session, username: str) -> Optional[UserModel]:
    return db.query(UserModel).filter(UserModel.username == username).first()


def list_all(db: Session) -> List[UserModel]:
    return db.query(UserModel).all()


def get_stats(db: Session, user_id: int) -> Optional[dict]:
    user = get_by_id(db, user_id)
    if not user:
        return None
    sub_count = db.query(SubscriptionModel).filter(SubscriptionModel.user_id == user_id).count()
    post_count = db.query(PostModel).filter(PostModel.author_id == user_id).count()
    return {
        "user_id": user_id,
        "username": user.username,
        "post_karma": user.post_karma,
        "comment_karma": user.comment_karma,
        "total_karma": user.total_karma,
        "subscriptions": sub_count,
        "posts_created": post_count,
        "feed_size": 0,
        "feed_sort": "hot",
    }


def update_location(db: Session, user_id: int, location: Location) -> bool:
    user = get_by_id(db, user_id)
    if not user:
        return False
    user.latitude = location.latitude
    user.longitude = location.longitude
    user.city = location.city
    user.region = location.region
    user.country = location.country
    user.geohash = geohash_encode(location.latitude, location.longitude)
    db.commit()
    db.refresh(user)
    return True


def get_subscribed_ids(db: Session, user_id: int) -> List[int]:
    rows = db.query(SubscriptionModel).filter(SubscriptionModel.user_id == user_id).all()
    return [row.subreddit_id for row in rows]
