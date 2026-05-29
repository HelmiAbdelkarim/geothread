from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from src.core.models import UserModel


def register(db: Session, username: str, email: str) -> Optional[UserModel]:
    if db.query(UserModel).filter(UserModel.username == username).first():
        return None
    user = UserModel(username=username, email=email, created_at=datetime.now())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_by_username(db: Session, username: str) -> Optional[UserModel]:
    return db.query(UserModel).filter(UserModel.username == username).first()
