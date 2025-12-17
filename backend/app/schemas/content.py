from pydantic import BaseModel, HttpUrl
from typing import Optional
from uuid import UUID
from datetime import date

class CreateContentRequest(BaseModel):
    url: HttpUrl
    tone: str
    emoji_usage: str

class ContentStatusResponse(BaseModel):
    id: UUID
    status: str
    message: Optional[str] = None
    error: Optional[str] = None # For debugging
    post_count: int = 0
    content_source: str = "transcript"

class PostResponse(BaseModel):
    id: UUID
    platform: str
    content: str
    included: bool

class SchedulePreviewResponse(BaseModel):
    id: UUID
    date: date
    platform: str
    preview: str
