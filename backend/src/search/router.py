from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.posts.schemas import PostResponse
from src.search import service
from src.search.schemas import SearchResponse
from src.subreddits.schemas import SubredditResponse
from src.users.schemas import UserResponse

router = APIRouter(prefix="/api/search", tags=["Search"])


def _post_response(post) -> PostResponse:
    return PostResponse(
        post_id=post.post_id, author_id=post.author_id, subreddit_id=post.subreddit_id,
        title=post.title, content=post.content, timestamp=post.timestamp,
        upvotes=post.upvotes, downvotes=post.downvotes, score=post.score,
        vote_ratio=post.vote_ratio, comments=post.comments,
        latitude=post.latitude, longitude=post.longitude, location_name=post.location_name,
    )


def _subreddit_response(sr) -> SubredditResponse:
    return SubredditResponse(
        subreddit_id=sr.subreddit_id, name=sr.name, description=sr.description,
        created_at=sr.created_at, subscriber_count=sr.subscriber_count, topic=sr.topic,
    )


def _user_response(user) -> UserResponse:
    return UserResponse(
        user_id=user.user_id, username=user.username, email=user.email,
        created_at=user.created_at, post_karma=user.post_karma,
        comment_karma=user.comment_karma, total_karma=user.total_karma,
    )


@router.get("/", response_model=SearchResponse)
async def search_all(q: str = Query(..., min_length=1), limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    return SearchResponse(
        posts=[_post_response(p) for p in service.search_posts(db, q, limit)],
        subreddits=[_subreddit_response(s) for s in service.search_subreddits(db, q, limit)],
        users=[_user_response(u) for u in service.search_users(db, q, limit)],
    )


@router.get("/posts", response_model=List[PostResponse])
async def search_posts_endpoint(q: str = Query(..., min_length=1), limit: int = Query(25, ge=1, le=100), db: Session = Depends(get_db)):
    return [_post_response(p) for p in service.search_posts(db, q, limit)]


@router.get("/subreddits", response_model=List[SubredditResponse])
async def search_subreddits_endpoint(q: str = Query(..., min_length=1), limit: int = Query(25, ge=1, le=100), db: Session = Depends(get_db)):
    return [_subreddit_response(s) for s in service.search_subreddits(db, q, limit)]


@router.get("/users", response_model=List[UserResponse])
async def search_users_endpoint(q: str = Query(..., min_length=1), limit: int = Query(25, ge=1, le=100), db: Session = Depends(get_db)):
    return [_user_response(u) for u in service.search_users(db, q, limit)]
