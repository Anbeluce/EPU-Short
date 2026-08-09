from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from pathlib import Path

from app.database import get_session
from app.services import get_link_by_code, get_note_by_code
from app.config import settings

router = APIRouter(tags=["Web"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))
templates.env.globals["APP_NAME"] = settings.APP_NAME
templates.env.globals["APP_FOOTER"] = settings.APP_FOOTER

@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"base_url": settings.BASE_URL})

@router.get("/note", response_class=HTMLResponse)
def note_index(request: Request):
    return templates.TemplateResponse(request=request, name="note_index.html", context={"base_url": settings.BASE_URL})

@router.get("/stats/link/{code}", response_class=HTMLResponse)
def link_stats(request: Request, code: str, session: Session = Depends(get_session)):
    link = get_link_by_code(session, code)
    if not link:
        return templates.TemplateResponse(request=request, name="error.html", context={"base_url": settings.BASE_URL, "error_title": "404 Không tìm thấy", "error_message": "Link không tồn tại hoặc đã hết hạn"}, status_code=404)
    return templates.TemplateResponse(request=request, name="stats.html", context={"base_url": settings.BASE_URL, "type": "link", "item": link})

@router.get("/stats/note/{code}", response_class=HTMLResponse)
def note_stats(request: Request, code: str, session: Session = Depends(get_session)):
    note = get_note_by_code(session, code)
    if not note:
        return templates.TemplateResponse(request=request, name="error.html", context={"base_url": settings.BASE_URL, "error_title": "404 Không tìm thấy", "error_message": "Note không tồn tại hoặc đã hết hạn"}, status_code=404)
    return templates.TemplateResponse(request=request, name="stats.html", context={"base_url": settings.BASE_URL, "type": "note", "item": note})
