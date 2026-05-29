import math
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session

from src.core.database import SubredditRecommendation, haversine_distance
from src.core.models import PostModel, SubredditModel, SubscriptionModel, UserModel


def get_by_id(db: Session, subreddit_id: int) -> Optional[SubredditModel]:
    return db.query(SubredditModel).filter(SubredditModel.subreddit_id == subreddit_id).first()


def get_by_name(db: Session, name: str) -> Optional[SubredditModel]:
    return db.query(SubredditModel).filter(SubredditModel.name.ilike(name)).first()


def list_all(db: Session) -> List[SubredditModel]:
    return db.query(SubredditModel).all()


def create(db: Session, name: str, description: str, topic: Optional[str] = None) -> SubredditModel:
    sr = SubredditModel(name=name, description=description, topic=topic, created_at=datetime.now())
    db.add(sr)
    db.commit()
    db.refresh(sr)
    return sr


def get_posts(db: Session, subreddit_id: int) -> List[PostModel]:
    return db.query(PostModel).filter(PostModel.subreddit_id == subreddit_id).all()


def get_online_count(db: Session, subreddit_id: int) -> int:
    from src.core.models import CommentModel
    cutoff = datetime.now() - timedelta(hours=24)
    sub_ids = {r[0] for r in db.query(SubscriptionModel.user_id).filter(SubscriptionModel.subreddit_id == subreddit_id)}
    poster_ids = {r[0] for r in db.query(PostModel.author_id).filter(PostModel.subreddit_id == subreddit_id, PostModel.timestamp >= cutoff)}
    commenter_ids = {
        r[0] for r in db.query(CommentModel.author_id).join(PostModel).filter(
            PostModel.subreddit_id == subreddit_id, CommentModel.created_at >= cutoff
        )
    }
    return len((poster_ids | commenter_ids) & sub_ids)


def subscribe(db: Session, user_id: int, subreddit_id: int) -> bool:
    sr = db.query(SubredditModel).filter(SubredditModel.subreddit_id == subreddit_id).first()
    if not sr:
        return False
    existing = db.query(SubscriptionModel).filter(
        SubscriptionModel.user_id == user_id, SubscriptionModel.subreddit_id == subreddit_id
    ).first()
    if existing:
        return True
    db.add(SubscriptionModel(user_id=user_id, subreddit_id=subreddit_id))
    sr.subscriber_count += 1
    db.commit()
    return True


def unsubscribe(db: Session, user_id: int, subreddit_id: int) -> bool:
    sr = db.query(SubredditModel).filter(SubredditModel.subreddit_id == subreddit_id).first()
    if not sr:
        return False
    existing = db.query(SubscriptionModel).filter(
        SubscriptionModel.user_id == user_id, SubscriptionModel.subreddit_id == subreddit_id
    ).first()
    if not existing:
        return False
    db.delete(existing)
    sr.subscriber_count = max(0, sr.subscriber_count - 1)
    db.commit()
    return True


def get_recommendations(db: Session, user_id: int, limit: int = 10) -> List[SubredditRecommendation]:
    user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    subscribed_ids = {r[0] for r in db.query(SubscriptionModel.subreddit_id).filter(SubscriptionModel.user_id == user_id)}
    user_topic_ids = {r[0] for r in db.query(SubscriptionModel.subreddit_id).filter(SubscriptionModel.user_id == user_id)}
    user_topics = {
        r[0].lower() for r in
        db.query(SubredditModel.topic).filter(SubredditModel.subreddit_id.in_(user_topic_ids))
        if r[0]
    }

    user_lat = user.latitude if user else None
    user_lng = user.longitude if user else None

    cutoff = datetime.now() - timedelta(days=30)
    results = []

    for sr in db.query(SubredditModel).all():
        if sr.subreddit_id in subscribed_ids:
            continue

        # Distance score (exponential decay — location-based algorithm)
        distance = None
        if user_lat is not None and sr.scope_lat is not None:
            distance = haversine_distance(user_lat, user_lng, sr.scope_lat, sr.scope_lng)
            if sr.scope_radius_km and distance > sr.scope_radius_km * 2:
                continue
        d_score = max(0.0, min(1.0, math.exp(-0.01 * distance))) if distance is not None else 0.5

        # Activity score (logarithmic scaling)
        recent = db.query(PostModel).filter(
            PostModel.subreddit_id == sr.subreddit_id, PostModel.timestamp >= cutoff
        ).count()
        a_score = min(1.0, recent / 10.0)
        if sr.subscriber_count > 0:
            a_score = (a_score + math.log10(sr.subscriber_count + 1) / 6.0) / 2.0

        # Relevance score (topic match)
        r_score = 0.9 if (sr.topic and sr.topic.lower() in user_topics) else 0.5

        total = d_score * 0.4 + a_score * 0.3 + r_score * 0.3

        parts = []
        if distance is not None:
            if distance < 10:
                parts.append(f"Very close ({distance:.1f} km away)")
            elif distance < 50:
                parts.append(f"Nearby ({distance:.1f} km away)")
        if a_score > 0.7:
            parts.append("Very active community")
        elif a_score > 0.4:
            parts.append("Active community")
        if r_score > 0.7:
            parts.append("Matches your interests")
        if sr.subscriber_count > 10000:
            parts.append(f"{sr.subscriber_count:,} members")

        results.append(SubredditRecommendation(
            subreddit_id=sr.subreddit_id, subreddit_name=sr.name,
            total_score=total, distance_km=distance,
            distance_score=d_score, activity_score=a_score, relevance_score=r_score,
            reason=" • ".join(parts) or "Popular community",
        ))

    results.sort(key=lambda x: x.total_score, reverse=True)
    return results[:limit]
