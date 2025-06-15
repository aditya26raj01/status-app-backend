from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    email: str
    full_name: str
    photo_url: Optional[str] = None
