from typing import Optional

from fastapi import Header, HTTPException, status

from src.core.database import reddit_db


async def get_current_user_id(x_user_id: Optional[int] = Header(None)) -> int:
    if x_user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-User-Id header.")
    if not reddit_db.get_user(x_user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {x_user_id} not found.")
    return x_user_id


async def get_optional_user_id(x_user_id: Optional[int] = Header(None)) -> Optional[int]:
    return x_user_id
