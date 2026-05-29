from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, Query, Response, status

from src.core.database import reddit_db
from src.core.dependencies import get_current_user_id, get_optional_user_id
from src.core.exceptions import BadRequestError, NotFoundError
from src.core.schemas import MessageResponse
from src.posts import service
from src.posts.schemas import FeedPostResponse, PostCreateRequest, PostResponse, VoteRequest

router = APIRouter(prefix="/api/posts", tags=["Posts"])

_VOTE_MESSAGES = {"up": "Upvoted", "down": "Downvoted", "remove": "Vote removed"}


def _set_pagination_headers(response: Response, total: int, limit: int, offset: int) -> None:
    next_offset = offset + limit
    has_more = next_offset < total
    response.headers["X-Total-Count"] = str(total)
    response.headers["X-Limit"] = str(limit)
    response.headers["X-Offset"] = str(offset)
    response.headers["X-Next-Offset"] = str(next_offset if has_more else "")
    response.headers["X-Has-More"] = str(has_more).lower()


def _to_response(post) -> PostResponse:
    return PostResponse(
        post_id=post.post_id, author_id=post.author_id, subreddit_id=post.subreddit_id,
        title=post.title, content=post.content,
        timestamp=post.timestamp,
        upvotes=post.upvotes, downvotes=post.downvotes, score=post.score,
        vote_ratio=post.vote_ratio, comments=post.comments, share_count=post.share_count,
        latitude=post.latitude, longitude=post.longitude,
    )


def _to_feed_response(post, user_id, distance_km: Optional[float] = None) -> FeedPostResponse:
    author = reddit_db.get_user(post.author_id)
    subreddit = reddit_db.get_subreddit(post.subreddit_id)
    return FeedPostResponse(
        **_to_response(post).model_dump(),
        author_username=author.username if author else "[deleted]",
        subreddit_name=subreddit.name if subreddit else "[deleted]",
        user_vote=service.get_vote(post.post_id, user_id) if user_id else 0,
        distance_km=round(distance_km, 3) if distance_km is not None else None,
    )


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(body: PostCreateRequest, user_id: int = Depends(get_current_user_id)):
    post = service.create(
        user_id,
        body.subreddit_id,
        body.title,
        body.content,
        body.latitude,
        body.longitude,
    )
    if not post:
        raise BadRequestError("Failed to create post. Check subreddit ID.")
    return _to_response(post)


@router.get("/", response_model=List[FeedPostResponse])
async def get_feed(
    response: Response,
    user_id: int = Depends(get_current_user_id),
    sort: Literal["hot", "new", "top", "rising", "controversial", "closest"] = Query("hot"),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    radius_km: Optional[float] = Query(None, gt=0, le=20000),
    latitude: Optional[float] = Query(None, ge=-90, le=90),
    longitude: Optional[float] = Query(None, ge=-180, le=180),
):
    if (latitude is None) != (longitude is None):
        raise BadRequestError("latitude and longitude must be provided together.")
    if sort == "closest":
        posts = service.get_closest_feed(user_id, limit, radius_km, latitude, longitude)
        return [_to_feed_response(post, user_id, distance) for post, distance in posts]
    total = service.get_feed_count(user_id)
    _set_pagination_headers(response, total, limit, offset)
    return [_to_feed_response(p, user_id) for p in service.get_feed(user_id, sort, limit, offset)]


@router.get("/user/{user_id}", response_model=List[PostResponse])
async def get_user_posts(
    user_id: int,
    response: Response,
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    posts = list(reversed(service.get_user_posts(user_id)))
    _set_pagination_headers(response, len(posts), limit, offset)
    return [_to_response(p) for p in posts[offset:offset + limit]]


@router.get("/{post_id}", response_model=FeedPostResponse)
async def get_post(post_id: int, user_id: int = Depends(get_optional_user_id)):
    post = service.get_by_id(post_id)
    if not post:
        raise NotFoundError(f"Post {post_id} not found.")
    return _to_feed_response(post, user_id)


@router.post("/{post_id}/vote", response_model=MessageResponse)
async def vote_on_post(post_id: int, body: VoteRequest, user_id: int = Depends(get_current_user_id)):
    if not service.get_by_id(post_id):
        raise NotFoundError(f"Post {post_id} not found.")
    service.vote(post_id, user_id, body.direction)
    return MessageResponse(message=_VOTE_MESSAGES[body.direction], success=True)


@router.post("/{post_id}/share", response_model=FeedPostResponse)
async def share_post(post_id: int, user_id: int = Depends(get_current_user_id)):
    if not service.share(post_id, user_id):
        raise NotFoundError(f"Post {post_id} not found.")
    return _to_feed_response(service.get_by_id(post_id), user_id)
