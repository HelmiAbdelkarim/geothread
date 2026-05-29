from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    sort: Optional[Literal["hot", "new", "top", "rising", "controversial"]] = "hot"
