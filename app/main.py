from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from pathlib import Path

from app.database import create_db_and_tables
from app.routers import shortlink, note, admin, api, web
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="EPU", lifespan=lifespan)

static_dir = Path(__file__).resolve().parent / "static"
if not static_dir.exists():
    static_dir.mkdir(parents=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

templates_dir = Path(__file__).resolve().parent / "templates"
if not templates_dir.exists():
    templates_dir.mkdir(parents=True)

templates = Jinja2Templates(directory=str(templates_dir))

# Include routers in correct order
app.include_router(note.router)
app.include_router(admin.router)
app.include_router(api.router)
app.include_router(web.router)
app.include_router(shortlink.router)

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={"base_url": settings.BASE_URL, "error_title": "404 Không tìm thấy", "error_message": "Trang bạn tìm không tồn tại"},
        status_code=404
    )
