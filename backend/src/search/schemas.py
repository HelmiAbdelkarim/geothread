from typing import List

from pydantic import BaseModel

from src.posts.schemas import PostResponse
from src.subreddits.schemas import SubredditResponse
from src.users.schemas import UserResponse


class SearchResponse(BaseModel):
    posts: List[PostResponse]
    subreddits: List[SubredditResponse]
    users: List[UserResponse]

