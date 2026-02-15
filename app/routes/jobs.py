from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.database import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/jobs")
async def list_jobs(request: Request):
    conn = get_db()
    jobs = conn.execute(
        "SELECT * FROM jobs ORDER BY date_posted DESC LIMIT 50"
    ).fetchall()
    conn.close()
    return templates.TemplateResponse("jobs.html", {
        "request": request,
        "jobs": jobs,
    })