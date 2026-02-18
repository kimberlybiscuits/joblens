from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.database import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/jobs")
async def list_jobs(request: Request, q: str = ""):
    conn = get_db()
    if q:
        jobs = conn.execute(
            """SELECT * FROM jobs
                WHERE title LIKE ? OR company LIKE ? OR tags LIKE
?
                ORDER BY created_at DESC LIMIT 100""",
            (f"%{q}%", f"%{q}%", f"%{q}%"),
        ).fetchall()
    else:
        jobs = conn.execute(
            "SELECT * FROM jobs ORDER BY created_at DESC LIMIT 100"
        ).fetchall()
    conn.close()
    return templates.TemplateResponse("jobs.html", {
        "request": request,
        "jobs": jobs,
        "q": q,
    })

from app.scheduler import fetch_all_jobs                                                                                       
                                                                                                                                 
@router.post("/jobs/fetch")                                                                                                    
def trigger_fetch():                                                                                                           
    # Run the scraper fetch in the background so the request returns immediately                                               
    # rather than making the browser wait 30-60 seconds for all scrapers to finish.
    import threading
    thread = threading.Thread(target=fetch_all_jobs)
    thread.daemon = True  # thread won't block the app from shutting down
    thread.start()
    return {"message": "Fetch started"}