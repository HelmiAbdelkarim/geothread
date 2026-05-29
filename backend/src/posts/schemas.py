from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


class PostCreateRequest(BaseModel):
    subreddit_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=300)
    content: str = Field("", max_length=40000)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)

    @model_validator(mode="after")
    def validate_coordinates(self):
        has_latitude = self.latitude is not None
        has_longitude = self.longitude is not None
        if has_latitude != has_longitude:
            raise ValueError("latitude and longitude must be provided together")
        return self


class PostResponse(BaseModel):
    post_id: int
    author_id: int
    subreddit_id: int
    title: str
    content: str
    timestamp: datetime
    upvotes: int
    downvotes: int
    score: int
    vote_ratio: float
    comments: int
    share_count: int = 0
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    class Config:
        from_attributes = True


class FeedPostResponse(PostResponse):
    author_username: str
    subreddit_name: str
    user_vote: int
    distance_km: Optional[float] = None


class VoteRequest(BaseModel):
    direction: Literal["up", "down", "remove"]
