from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    photo_url: Optional[str] = None

class TelegramAuthData(BaseModel):
    id: int
    first_name: str
    auth_date: int
    hash: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None

class ShortUserResponse(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    photo_url: Optional[str] = None

class FullUserResponse(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    photo_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class UserUpdate(BaseModel):
    username: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    photo_url: Optional[str] = None
