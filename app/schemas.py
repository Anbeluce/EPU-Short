from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class ShortenRequest(BaseModel):
    url: str
    custom_code: Optional[str] = None
    expires_at: Optional[datetime] = None

class ShortenResponse(BaseModel):
    short_code: str
    short_url: str
    original_url: str
    has_password: bool
    expires_at: Optional[datetime]
    created_at: datetime

class NoteCreateRequest(BaseModel):
    title: Optional[str] = None
    content: str
    custom_code: Optional[str] = None
    password: Optional[str] = None
    expires_at: Optional[datetime] = None

class NoteCreateResponse(BaseModel):
    short_code: str
    note_url: str
    title: Optional[str]
    has_password: bool
    expires_at: Optional[datetime]
    created_at: datetime

class StatsResponse(BaseModel):
    short_code: str
    original_url: Optional[str] = None
    title: Optional[str] = None
    is_active: bool
    click_count: Optional[int] = None
    view_count: Optional[int] = None
    has_password: bool
    created_at: datetime
    expires_at: Optional[datetime]

class ErrorResponse(BaseModel):
    detail: str
