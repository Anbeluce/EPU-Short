from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from pathlib import Path

from app.database import get_session
from app.services import get_link_by_code, increment_link_clicks
from app.utils import verify_password
from app.config import settings

router = APIRouter(prefix="", tags=["ShortLink"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))
templates.env.globals["APP_NAME"] = settings.APP_NAME
templates.env.globals["APP_FOOTER"] = settings.APP_FOOTER

@router.get("/{code}", response_class=HTMLResponse)
def redirect_link(request: Request, code: str, session: Session = Depends(get_session)):
    link = get_link_by_code(session, code)
    if not link:
        return templates.TemplateResponse(request=request, name="error.html", context={"base_url": settings.BASE_URL, "error_title": "404 Không tìm thấy", "error_message": "Link không tồn tại hoặc đã hết hạn"}, status_code=404)
        
    if not link.password_hash:
        increment_link_clicks(session, link)
        return RedirectResponse(url=link.original_url, status_code=307)
        
    return templates.TemplateResponse(request=request, name="password.html", context={"base_url": settings.BASE_URL, "type": "link", "code": code})

@router.post("/{code}")
def verify_link_password(request: Request, code: str, password: str = Form(...), session: Session = Depends(get_session)):
    link = get_link_by_code(session, code)
    if not link:
        return templates.TemplateResponse(request=request, name="error.html", context={"base_url": settings.BASE_URL, "error_title": "404 Không tìm thấy", "error_message": "Link không tồn tại hoặc đã hết hạn"}, status_code=404)
        
    if not link.password_hash:
        increment_link_clicks(session, link)
        return RedirectResponse(url=link.original_url, status_code=307)
        
    if verify_password(password, link.password_hash):
        increment_link_clicks(session, link)
        return RedirectResponse(url=link.original_url, status_code=307)
        
    return templates.TemplateResponse(request=request, name="password.html", context={"base_url": settings.BASE_URL, "type": "link", "code": code, "error": "Mật khẩu không đúng"})
