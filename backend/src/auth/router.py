from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.auth import service
from src.auth.schemas import RegisterRequest
from src.core.db import get_db
from src.core.exceptions import BadRequestError, NotFoundError
from src.users.schemas import UserResponse

router = APIRouter(prefix="/api/auth", tags=["Auth"])


def _to_response(user) -> UserResponse:
    return UserResponse(
        user_id=user.user_id, username=user.username, email=user.email,
        created_at=user.created_at, post_karma=user.post_karma,
        comment_karma=user.comment_karma, total_karma=user.total_karma,
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: Session = Depends(get_db)):
    user = service.register(db, body.username, body.email)
    if not user:
        raise BadRequestError(f"Username '{body.username}' is already taken.")
    return _to_response(user)


@router.post("/login", response_model=UserResponse)
async def login(username: str, db: Session = Depends(get_db)):
    user = service.get_by_username(db, username)
    if not user:
        raise NotFoundError(f"User '{username}' not found.")
    return _to_response(user)
