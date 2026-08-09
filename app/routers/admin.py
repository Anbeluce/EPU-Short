from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from pathlib import Path
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from datetime import datetime, timezone

from app.database import get_session
from app.services import get_all_links, get_all_notes, toggle_link_active, toggle_note_active, delete_link, delete_note, get_overview_stats
from app.config import settings

router = APIRouter(prefix="/memaybeo", tags=["Admin"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))
templates.env.globals["APP_NAME"] = settings.APP_NAME
templates.env.globals["APP_FOOTER"] = settings.APP_FOOTER

serializer = URLSafeTimedSerializer(settings.SECRET_KEY)

def require_admin(request: Request):
    token = request.cookies.get("admin_session")
    if not token:
        return None
    try:
        user = serializer.loads(token, max_age=settings.SESSION_MAX_AGE)
        if user == settings.ADMIN_USERNAME:
            return user
    except (SignatureExpired, BadSignature):
        pass
    return None

@router.get("/", response_class=HTMLResponse)
def admin_login_page(request: Request):
    user = require_admin(request)
    if user:
        return RedirectResponse(url="/memaybeo/dashboard", status_code=303)
    return templates.TemplateResponse(request=request, name="admin/login.html", context={"base_url": settings.BASE_URL})

@router.post("/login")
def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD:
        token = serializer.dumps(username)
        response = RedirectResponse(url="/memaybeo/dashboard", status_code=303)
        response.set_cookie(key="admin_session", value=token, httponly=True, max_age=settings.SESSION_MAX_AGE)
        return response
    return templates.TemplateResponse(request=request, name="admin/login.html", context={
        "base_url": settings.BASE_URL,
        "error": "Sai tên đăng nhập hoặc mật khẩu"
    })

@router.get("/dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request, session: Session = Depends(get_session)):
    user = require_admin(request)
    if not user:
        return RedirectResponse(url="/memaybeo", status_code=303)
        
    stats = get_overview_stats(session)
    links = get_all_links(session)
    notes = get_all_notes(session)
    
    return templates.TemplateResponse(request=request, name="admin/dashboard.html", context={
        "base_url": settings.BASE_URL,
        "stats": stats,
        "links": links,
        "notes": notes,
        "now": datetime.now(timezone.utc).replace(tzinfo=None)
    })

@router.post("/toggle/{item_type}/{item_id}")
def admin_toggle(request: Request, item_type: str, item_id: int, session: Session = Depends(get_session)):
    user = require_admin(request)
    if not user:
        return RedirectResponse(url="/memaybeo", status_code=303)
        
    if item_type == "link":
        toggle_link_active(session, item_id)
    elif item_type == "note":
        toggle_note_active(session, item_id)
        
    return RedirectResponse(url="/memaybeo/dashboard", status_code=303)

@router.post("/delete/{item_type}/{item_id}")
def admin_delete(request: Request, item_type: str, item_id: int, session: Session = Depends(get_session)):
    user = require_admin(request)
    if not user:
        return RedirectResponse(url="/memaybeo", status_code=303)
        
    if item_type == "link":
        delete_link(session, item_id)
    elif item_type == "note":
        delete_note(session, item_id)
        
    return RedirectResponse(url="/memaybeo/dashboard", status_code=303)

@router.get("/logout")
def admin_logout():
    response = RedirectResponse(url="/memaybeo", status_code=303)
    response.delete_cookie("admin_session")
    return response
