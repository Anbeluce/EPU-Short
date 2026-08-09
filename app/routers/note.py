from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from pathlib import Path

from app.database import get_session
from app.services import get_note_by_code, increment_note_views
from app.utils import verify_password
from app.config import settings

router = APIRouter(prefix="/n", tags=["Note"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))
templates.env.globals["APP_NAME"] = settings.APP_NAME
templates.env.globals["APP_FOOTER"] = settings.APP_FOOTER

@router.get("/{code}", response_class=HTMLResponse)
def view_note(request: Request, code: str, session: Session = Depends(get_session)):
    note = get_note_by_code(session, code)
    if not note:
        return templates.TemplateResponse(request=request, name="error.html", context={"base_url": settings.BASE_URL, "error_title": "404 Không tìm thấy", "error_message": "Note không tồn tại hoặc đã hết hạn"}, status_code=404)
        
    if not note.password_hash:
        increment_note_views(session, note)
        return templates.TemplateResponse(request=request, name="note_view.html", context={"base_url": settings.BASE_URL, "note": note})
        
    return templates.TemplateResponse(request=request, name="password.html", context={"base_url": settings.BASE_URL, "type": "note", "code": code})

@router.post("/{code}", response_class=HTMLResponse)
def verify_note_password(request: Request, code: str, password: str = Form(...), session: Session = Depends(get_session)):
    note = get_note_by_code(session, code)
    if not note:
        return templates.TemplateResponse(request=request, name="error.html", context={"base_url": settings.BASE_URL, "error_title": "404 Không tìm thấy", "error_message": "Note không tồn tại hoặc đã hết hạn"}, status_code=404)
        
    if not note.password_hash:
        increment_note_views(session, note)
        return templates.TemplateResponse(request=request, name="note_view.html", context={"base_url": settings.BASE_URL, "note": note})
        
    if verify_password(password, note.password_hash):
        increment_note_views(session, note)
        return templates.TemplateResponse(request=request, name="note_view.html", context={"base_url": settings.BASE_URL, "note": note})
        
    return templates.TemplateResponse(request=request, name="password.html", context={"base_url": settings.BASE_URL, "type": "note", "code": code, "error": "Mật khẩu không đúng"})
