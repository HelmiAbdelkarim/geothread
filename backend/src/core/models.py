import math
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    post_karma = Column(Integer, nullable=False, default=0)
    comment_karma = Column(Integer, nullable=False, default=0)
    latitude = Column(Float)
    longitude = Column(Float)
    city = Column(String(200))
    region = Column(String(200))
    country = Column(String(200))
    geohash = Column(String(20))

    subscriptions = relationship("SubscriptionModel", back_populates="user", lazy="select")
    posts = relationship("PostModel", foreign_keys="PostModel.author_id", back_populates="author", lazy="select")

    @property
    def total_karma(self) -> int:
        return self.post_karma + self.comment_karma


class SubredditModel(Base):
    __tablename__ = "subreddits"

    subreddit_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, default="")
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    topic = Column(String(100))
    subscriber_count = Column(Integer, nullable=False, default=0)
    # Location scope stored flat
    scope_type = Column(String(20))   # "city" | "region" | "country" | "global" | None
    scope_lat = Column(Float)
    scope_lng = Column(Float)
    scope_radius_km = Column(Float)
    scope_region = Column(String(200))
    scope_country = Column(String(200))
    scope_geohash = Column(String(20))
    activity_score = Column(Float, default=0.0)

    subscriptions = relationship("SubscriptionModel", back_populates="subreddit", lazy="select")
    post_rows = relationship("PostModel", back_populates="subreddit", lazy="select")


class SubscriptionModel(Base):
    __tablename__ = "subscriptions"

    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    subreddit_id = Column(Integer, ForeignKey("subreddits.subreddit_id", ondelete="CASCADE"), primary_key=True)

    user = relationship("UserModel", back_populates="subscriptions")
    subreddit = relationship("SubredditModel", back_populates="subscriptions")


class PostModel(Base):
    __tablename__ = "posts"

    post_id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    subreddit_id = Column(Integer, ForeignKey("subreddits.subreddit_id"), nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(Text, default="")
    timestamp = Column(DateTime, nullable=False, default=datetime.now)
    upvotes = Column(Integer, nullable=False, default=0)
    downvotes = Column(Integer, nullable=False, default=0)
    comment_count = Column(Integer, nullable=False, default=0)
    share_count = Column(Integer, nullable=False, default=0)
    latitude = Column(Float)
    longitude = Column(Float)
    location_name = Column(String(300))

    author = relationship("UserModel", back_populates="posts")
    subreddit = relationship("SubredditModel", back_populates="post_rows")
    vote_rows = relationship("PostVoteModel", back_populates="post", lazy="select")
    comment_rows = relationship("CommentModel", back_populates="post", lazy="select")

    @property
    def comments(self) -> int:
        return self.comment_count

    @property
    def score(self) -> int:
        return self.upvotes - self.downvotes

    @property
    def vote_ratio(self) -> float:
        total = self.upvotes + self.downvotes
        return self.upvotes / total if total else 0.5

    @property
    def location(self) -> Optional[object]:
        if self.latitude is None or self.longitude is None:
            return None
        from src.core.database import Location
        return Location(self.latitude, self.longitude)

    def calculate_hot_score(self) -> float:
        s = self.score
        order = math.log10(max(abs(s), 1))
        sign = 1 if s > 0 else (-1 if s < 0 else 0)
        seconds = (self.timestamp - datetime(1970, 1, 1)).total_seconds()
        return round(sign * order + seconds / 45000, 7)

    def calculate_controversial_score(self) -> float:
        if not self.upvotes or not self.downvotes:
            return 0.0
        magnitude = self.upvotes + self.downvotes
        balance = min(self.upvotes, self.downvotes) / max(self.upvotes, self.downvotes)
        return magnitude * balance

    def calculate_priority(self, strategy: str = "hot") -> float:
        if strategy == "hot":
            return self.calculate_hot_score()
        if strategy == "new":
            return (self.timestamp - datetime(1970, 1, 1)).total_seconds()
        if strategy == "top":
            return float(self.score)
        if strategy == "rising":
            age_hours = (datetime.now() - self.timestamp).total_seconds() / 3600
            return 0.0 if age_hours > 24 else self.score / (age_hours + 2) ** 1.5
        if strategy == "controversial":
            return self.calculate_controversial_score()
        return 0.0


class PostVoteModel(Base):
    __tablename__ = "post_votes"

    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.post_id", ondelete="CASCADE"), primary_key=True)
    value = Column(Integer, nullable=False)  # 1 or -1

    post = relationship("PostModel", back_populates="vote_rows")


class CommentModel(Base):
    __tablename__ = "comments"

    comment_id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.user_id"))
    post_id = Column(Integer, ForeignKey("posts.post_id", ondelete="CASCADE"))
    parent_comment_id = Column(Integer, ForeignKey("comments.comment_id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now)
    is_edited = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    upvotes = Column(Integer, nullable=False, default=0)
    downvotes = Column(Integer, nullable=False, default=0)

    author = relationship("UserModel")
    post = relationship("PostModel", back_populates="comment_rows")
    vote_rows = relationship("CommentVoteModel", back_populates="comment", lazy="select")

    @property
    def score(self) -> int:
        return self.upvotes - self.downvotes

    def to_dict(self) -> dict:
        return {
            "comment_id": self.comment_id,
            "content": self.content if not self.is_deleted else "[deleted]",
            "author_id": self.author_id if not self.is_deleted else None,
            "post_id": self.post_id,
            "parent_comment_id": self.parent_comment_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_edited": self.is_edited,
            "is_deleted": self.is_deleted,
            "upvotes": self.upvotes,
            "downvotes": self.downvotes,
            "score": self.score,
        }


class CommentVoteModel(Base):
    __tablename__ = "comment_votes"

    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    comment_id = Column(Integer, ForeignKey("comments.comment_id", ondelete="CASCADE"), primary_key=True)
    value = Column(Integer, nullable=False)  # 1 or -1

    comment = relationship("CommentModel", back_populates="vote_rows")
