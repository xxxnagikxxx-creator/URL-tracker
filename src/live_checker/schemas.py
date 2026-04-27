from pydantic import BaseModel
from datetime import datetime
from typing import List


class LinkCreate(BaseModel):
    url: str

class ShortLinkResponse(BaseModel):
    id: int
    url: str

class LinkCheckResponse(BaseModel):
    id: int
    link_id: int
    status_code: int
    response_time: float
    created_at: datetime

class LinkResponse(BaseModel):
    id: int
    url: str
    telegram_id: int
    created_at: datetime
    checks: List[LinkCheckResponse] = []

class LinksResponse(BaseModel):
    links: List[ShortLinkResponse]