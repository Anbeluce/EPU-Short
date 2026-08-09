from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field

def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)

class Link(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    short_code: str = Field(max_length=20, unique=True, index=True)
    original_url: str
    password_hash: Optional[str] = None
    is_active: bool = Field(default=True)
    click_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=utcnow)
    expires_at: Optional[datetime] = None

class Note(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    short_code: str = Field(max_length=20, unique=True, index=True)
    title: Optional[str] = Field(default=None, max_length=200)
    content: str
    password_hash: Optional[str] = None
    is_active: bool = Field(default=True)
    view_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=utcnow)
    expires_at: Optional[datetime] = None
