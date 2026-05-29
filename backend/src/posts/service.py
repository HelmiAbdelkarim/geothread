import heapq
from datetime import datetime
from typing import List, Literal, Optional, Tuple

from sqlalchemy.orm import Session

from src.core.database import haversine_distance
from src.core.models import PostModel, PostVoteModel, SubscriptionModel, UserModel


def create(
    db: Session,
    author_id: int,
    subreddit_id: int,
    title: str,
    content: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    location_name: Optional[str] = None,
) -> Optional[PostModel]:
    post = PostModel(
        author_id=author_id, subreddit_id=subreddit_id,
        title=title, content=content, timestamp=datetime.now(),
        latitude=latitude, longitude=longitude, location_name=location_name,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def get_by_id(db: Session, post_id: int) -> Optional[PostModel]:
    return db.query(PostModel).filter(PostModel.post_id == post_id).first()


def get_user_posts(db: Session, user_id: int) -> List[PostModel]:
    return db.query(PostModel).filter(PostModel.author_id == user_id).order_by(PostModel.timestamp.desc()).all()


def get_feed(db: Session, user_id: Optional[int], sort: str, limit: int, offset: int = 0) -> List[PostModel]:
    """Heap-based priority sort (ASNAP algorithm).
    When user_id is None or user has no subscriptions, falls back to a global feed."""
    if user_id is not None:
        sub_ids = [r[0] for r in db.query(SubscriptionModel.subreddit_id).filter(SubscriptionModel.user_id == user_id)]
        posts = db.query(PostModel).filter(PostModel.subreddit_id.in_(sub_ids)).all() if sub_ids else []
    else:
        posts = []

    # Fall back to all posts if the user has no subscribed content
    if not posts:
        posts = db.query(PostModel).all()

    heap: list = []
    for post in posts:
        priority = post.calculate_priority(sort)
        heapq.heappush(heap, (-priority, post.post_id, post))

    ranked = [heapq.heappop(heap)[2] for _ in range(len(heap))]
    return ranked[offset:offset + limit]


def get_feed_count(db: Session, user_id: Optional[int]) -> int:
    if user_id is not None:
        sub_ids = [r[0] for r in db.query(SubscriptionModel.subreddit_id).filter(SubscriptionModel.user_id == user_id)]
        if sub_ids:
            count = db.query(PostModel).filter(PostModel.subreddit_id.in_(sub_ids)).count()
            if count:
                return count
    return db.query(PostModel).count()


def get_closest_feed(
    db: Session,
    user_id: int,
    limit: int,
    radius_km: Optional[float] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> List[Tuple[PostModel, float]]:
    if latitude is None or longitude is None:
        user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
        if not user or user.latitude is None:
            return []
        latitude, longitude = user.latitude, user.longitude

    sub_ids = [r[0] for r in db.query(SubscriptionModel.subreddit_id).filter(SubscriptionModel.user_id == user_id)]
    if not sub_ids:
        return []

    posts = db.query(PostModel).filter(
        PostModel.subreddit_id.in_(sub_ids),
        PostModel.latitude.isnot(None),
        PostModel.longitude.isnot(None),
    ).all()

    ranked = []
    for post in posts:
        dist = haversine_distance(latitude, longitude, post.latitude, post.longitude)
        if radius_km is not None and dist > radius_km:
            continue
        ranked.append((dist, post))

    ranked.sort(key=lambda x: x[0])
    return [(post, dist) for dist, post in ranked[:limit]]


def vote(db: Session, post_id: int, user_id: int, direction: Literal["up", "down", "remove"]) -> None:
    post = db.query(PostModel).filter(PostModel.post_id == post_id).first()
    if not post:
        return
    row = db.query(PostVoteModel).filter(PostVoteModel.user_id == user_id, PostVoteModel.post_id == post_id).first()
    current = row.value if row else 0

    if direction == "up":
        new_val = 0 if current == 1 else 1
    elif direction == "down":
        new_val = 0 if current == -1 else -1
    else:
        new_val = 0

    if current == 1:
        post.upvotes -= 1
    elif current == -1:
        post.downvotes -= 1
    if new_val == 1:
        post.upvotes += 1
    elif new_val == -1:
        post.downvotes += 1

    if new_val == 0:
        if row:
            db.delete(row)
    elif row:
        row.value = new_val
    else:
        db.add(PostVoteModel(user_id=user_id, post_id=post_id, value=new_val))

    # Recalculate author karma from all their posts
    author = db.query(UserModel).filter(UserModel.user_id == post.author_id).first()
    if author:
        author.post_karma = sum(
            p.upvotes - p.downvotes
            for p in db.query(PostModel).filter(PostModel.author_id == post.author_id).all()
        )

    db.commit()


def get_vote(db: Session, post_id: int, user_id: int) -> int:
    if not user_id:
        return 0
    row = db.query(PostVoteModel).filter(PostVoteModel.user_id == user_id, PostVoteModel.post_id == post_id).first()
    return row.value if row else 0


def share(db: Session, post_id: int, user_id: int) -> bool:
    post = db.query(PostModel).filter(PostModel.post_id == post_id).first()
    if not post:
        return False
    post.share_count += 1
    db.commit()
    return True
