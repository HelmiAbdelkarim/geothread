from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.core.database import Location
from src.core.db import get_db
from src.core.dependencies import get_current_user_id
from src.core.exceptions import NotFoundError
from src.users import service
from src.users.schemas import LocationUpdateRequest, UserResponse, UserStatsResponse

router = APIRouter(prefix="/api/users", tags=["Users"])


def _to_response(user) -> UserResponse:
    return UserResponse(
        user_id=user.user_id, username=user.username, email=user.email,
        created_at=user.created_at, post_karma=user.post_karma,
        comment_karma=user.comment_karma, total_karma=user.total_karma,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return _to_response(service.get_by_id(db, user_id))


@router.get("/me/stats", response_model=UserStatsResponse)
async def get_my_stats(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    stats = service.get_stats(db, user_id)
    if not stats:
        raise NotFoundError("User stats not found.")
    return UserStatsResponse(**stats)


@router.get("/me/subscriptions", response_model=List[int])
async def get_subscriptions(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return service.get_subscribed_ids(db, user_id)


@router.put("/me/location", response_model=UserResponse)
async def update_location(
    body: LocationUpdateRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    location = Location(body.latitude, body.longitude, body.city, body.region, body.country)
    service.update_location(db, user_id, location)
    return _to_response(service.get_by_id(db, user_id))


@router.get("/", response_model=List[UserResponse])
async def list_users(limit: int = Query(50), db: Session = Depends(get_db)):
    return [_to_response(u) for u in service.list_all(db)[:limit]]


@router.get("/{username}", response_model=UserResponse)
async def get_by_username(username: str, db: Session = Depends(get_db)):
    user = service.get_by_username(db, username)
    if not user:
        raise NotFoundError(f"User '{username}' not found.")
    return _to_response(user)
