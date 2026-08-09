from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.database import get_session
from app.schemas import ShortenRequest, ShortenResponse, NoteCreateRequest, NoteCreateResponse, StatsResponse, ErrorResponse
from app.services import create_short_link, create_note, get_link_by_code, get_note_by_code
from app.config import settings

router = APIRouter(prefix="/api", tags=["API"])

@router.post("/shorten", response_model=ShortenResponse, responses={400: {"model": ErrorResponse}})
def api_shorten(req: ShortenRequest, session: Session = Depends(get_session)):
    try:
        link = create_short_link(
            session=session,
            url=req.url,
            custom_code=req.custom_code,
            password=req.password,
            expires_in_hours=req.expires_in_hours
        )
        return ShortenResponse(
            short_code=link.short_code,
            short_url=f"{settings.BASE_URL}/{link.short_code}",
            original_url=link.original_url,
            has_password=bool(link.password_hash),
            expires_at=link.expires_at,
            created_at=link.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/note", response_model=NoteCreateResponse, responses={400: {"model": ErrorResponse}})
def api_create_note(req: NoteCreateRequest, session: Session = Depends(get_session)):
    try:
        note = create_note(
            session=session,
            content=req.content,
            title=req.title,
            custom_code=req.custom_code,
            password=req.password,
            expires_in_hours=req.expires_in_hours
        )
        return NoteCreateResponse(
            short_code=note.short_code,
            note_url=f"{settings.BASE_URL}/n/{note.short_code}",
            title=note.title,
            has_password=bool(note.password_hash),
            expires_at=note.expires_at,
            created_at=note.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/link/{code}", responses={404: {"model": ErrorResponse}})
def api_delete_link(code: str, session: Session = Depends(get_session)):
    link = get_link_by_code(session, code)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    link.is_active = False
    session.add(link)
    session.commit()
    return {"detail": "Link deactivated successfully"}

@router.delete("/note/{code}", responses={404: {"model": ErrorResponse}})
def api_delete_note(code: str, session: Session = Depends(get_session)):
    note = get_note_by_code(session, code)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    note.is_active = False
    session.add(note)
    session.commit()
    return {"detail": "Note deactivated successfully"}
