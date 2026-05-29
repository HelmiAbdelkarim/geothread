from typing import List

from fastapi import APIRouter, Query

from src.posts.schemas import PostResponse
from src.search import service
from src.search.schemas import SearchResponse
from src.subreddits.schemas import SubredditResponse
from src.users.schemas import UserResponse

router = APIRouter(prefix="/api/search", tags=["Search"])


def _post_response(post) -> PostResponse:
    return PostResponse(
        post_id=post.post_id,
        author_id=post.author_id,
        subreddit_id=post.subreddit_id,
        title=post.title,
        content=post.content,
        timestamp=post.timestamp,
        upvotes=post.upvotes,
        downvotes=post.downvotes,
        score=post.score,
        vote_ratio=post.vote_ratio,
        comments=post.comments,
    )


def _subreddit_response(subreddit) -> SubredditResponse:
    return SubredditResponse(
        subreddit_id=subreddit.subreddit_id,
        name=subreddit.name,
        description=subreddit.description,
        created_at=subreddit.created_at,
        subscriber_count=subreddit.subscriber_count,
    )


def _user_response(user) -> UserResponse:
    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        created_at=user.created_at,
        post_karma=user.post_karma,
        comment_karma=user.comment_karma,
        total_karma=user.total_karma,
    )


@router.get("/", response_model=SearchResponse)
async def search_all(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
):
    return SearchResponse(
        posts=[_post_response(post) for post in service.search_posts(q, limit)],
        subreddits=[_subreddit_response(subreddit) for subreddit in service.search_subreddits(q, limit)],
        users=[_user_response(user) for user in service.search_users(q, limit)],
    )


@router.get("/posts", response_model=List[PostResponse])
async def search_posts(
    q: str = Query(..., min_length=1),
    limit: int = Query(25, ge=1, le=100),
):
    return [_post_response(post) for post in service.search_posts(q, limit)]


@router.get("/subreddits", response_model=List[SubredditResponse])
async def search_subreddits(
    q: str = Query(..., min_length=1),
    limit: int = Query(25, ge=1, le=100),
):
    return [_subreddit_response(subreddit) for subreddit in service.search_subreddits(q, limit)]


@router.get("/users", response_model=List[UserResponse])
async def search_users(
    q: str = Query(..., min_length=1),
    limit: int = Query(25, ge=1, le=100),
):
    return [_user_response(user) for user in service.search_users(q, limit)]

