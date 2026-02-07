from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    display_name: str
    email: Optional[EmailStr] = None
    bio: Optional[str] = None
    avatar_path: Optional[str] = None  # optional on create

class User(BaseModel):
    id: int
    display_name: str
    email: Optional[EmailStr] = None
    bio: Optional[str] = None
    avatar_path: Optional[str] = None
    created_at: str
    last_active_at: Optional[str] = None