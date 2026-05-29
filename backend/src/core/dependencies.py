from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.core.models import UserModel


async def get_current_user_id(x_user_id: Optional[int] = Header(None), db: Session = Depends(get_db)) -> int:
    if x_user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-User-Id header.")
    user = db.query(UserModel).filter(UserModel.user_id == x_user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {x_user_id} not found.")
    return x_user_id


async def get_optional_user_id(x_user_id: Optional[int] = Header(None)) -> Optional[int]:
    return x_user_id
