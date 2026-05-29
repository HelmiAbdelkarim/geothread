from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SubredditCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=21, pattern="^[a-zA-Z0-9_]+$")
    description: str = Field(..., max_length=500)
    topic: Optional[str] = Field(default=None, min_length=1, max_length=80)


class SubredditResponse(BaseModel):
    subreddit_id: int
    name: str
    description: str
    created_at: datetime
    subscriber_count: int
    topic: Optional[str] = None

    class Config:
        from_attributes = True


class SubredditRecommendationResponse(BaseModel):
    subreddit_id: int
    subreddit_name: str
    total_score: float
    distance_km: Optional[float]
    distance_score: float
    activity_score: float
    relevance_score: float
    reason: str
