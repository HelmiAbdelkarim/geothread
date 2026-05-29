from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    created_at: datetime
    post_karma: int
    comment_karma: int
    total_karma: int

    class Config:
        from_attributes = True


class UserStatsResponse(BaseModel):
    user_id: int
    username: str
    post_karma: int
    comment_karma: int
    total_karma: int
    subscriptions: int
    posts_created: int
    feed_size: int
    feed_sort: str


class LocationUpdateRequest(BaseModel):
    latitude: float
    longitude: float
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
