from typing import List

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.core.dependencies import get_current_user_id
from src.core.exceptions import BadRequestError, NotFoundError
from src.core.schemas import MessageResponse
from src.posts.schemas import PostResponse
from src.subreddits import service
from src.subreddits.schemas import SubredditCreateRequest, SubredditRecommendationResponse, SubredditResponse

router = APIRouter(prefix="/api/subreddits", tags=["Subreddits"])


def _set_pagination_headers(response: Response, total: int, limit: int, offset: int) -> None:
    next_offset = offset + limit
    has_more = next_offset < total
    response.headers["X-Total-Count"] = str(total)
    response.headers["X-Limit"] = str(limit)
    response.headers["X-Offset"] = str(offset)
    response.headers["X-Next-Offset"] = str(next_offset if has_more else "")
    response.headers["X-Has-More"] = str(has_more).lower()


def _to_response(sr) -> SubredditResponse:
    return SubredditResponse(
        subreddit_id=sr.subreddit_id, name=sr.name, description=sr.description,
        created_at=sr.created_at, subscriber_count=sr.subscriber_count, topic=sr.topic,
    )


@router.post("/", response_model=SubredditResponse, status_code=status.HTTP_201_CREATED)
async def create_subreddit(
    body: SubredditCreateRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    if service.get_by_name(db, body.name):
        raise BadRequestError(f"Subreddit 'r/{body.name}' already exists.")
    return _to_response(service.create(db, body.name, body.description, body.topic))


@router.get("/recommendations", response_model=List[SubredditRecommendationResponse])
async def get_recommendations(
    user_id: int = Depends(get_current_user_id),
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db),
):
    return [SubredditRecommendationResponse(**vars(r)) for r in service.get_recommendations(db, user_id, limit)]


@router.get("/", response_model=List[SubredditResponse])
async def list_subreddits(db: Session = Depends(get_db)):
    return [_to_response(sr) for sr in service.list_all(db)]


@router.get("/{subreddit_id}", response_model=SubredditResponse)
async def get_subreddit(subreddit_id: int, db: Session = Depends(get_db)):
    sr = service.get_by_id(db, subreddit_id)
    if not sr:
        raise NotFoundError(f"Subreddit {subreddit_id} not found.")
    return _to_response(sr)


@router.post("/{subreddit_id}/subscribe", response_model=MessageResponse)
async def subscribe(
    subreddit_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    if not service.subscribe(db, user_id, subreddit_id):
        raise BadRequestError("Failed to subscribe. Subreddit may not exist.")
    sr = service.get_by_id(db, subreddit_id)
    return MessageResponse(message=f"Subscribed to r/{sr.name}", success=True)


@router.delete("/{subreddit_id}/subscribe", response_model=MessageResponse)
async def unsubscribe(
    subreddit_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    if not service.unsubscribe(db, user_id, subreddit_id):
        raise BadRequestError("Failed to unsubscribe.")
    sr = service.get_by_id(db, subreddit_id)
    return MessageResponse(message=f"Unsubscribed from r/{sr.name}", success=True)


@router.get("/{subreddit_id}/posts", response_model=List[PostResponse])
async def get_subreddit_posts(
    subreddit_id: int,
    response: Response,
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    posts = sorted(service.get_posts(db, subreddit_id), key=lambda p: p.score, reverse=True)
    _set_pagination_headers(response, len(posts), limit, offset)
    return [
        PostResponse(
            post_id=p.post_id, author_id=p.author_id, subreddit_id=p.subreddit_id,
            title=p.title, content=p.content, timestamp=p.timestamp,
            upvotes=p.upvotes, downvotes=p.downvotes, score=p.score,
            vote_ratio=p.vote_ratio, comments=p.comments, share_count=p.share_count,
            latitude=p.latitude, longitude=p.longitude, location_name=p.location_name,
        )
        for p in posts[offset:offset + limit]
    ]
