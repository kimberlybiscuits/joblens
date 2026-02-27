from fastapi import APIRouter, Request, Query
from fastapi.templating import Jinja2Templates
from typing import List
from app.database import get_db
from app.scheduler import fetch_all_jobs

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/jobs")                                                                                                                                
async def list_jobs(request: Request, q: str = "", location: str = "", remote: str = "", titles: List[str] = Query(default=[]), use_titles: str = ""):
    conn = get_db()

    # Load preferred titles from profile
    profile = conn.execute("SELECT preferred_titles FROM profiles LIMIT 1").fetchone()
    preferred_titles = []
    if profile and profile["preferred_titles"]:
        preferred_titles = [t.strip() for t in profile["preferred_titles"].split(",") if t.strip()]

    # On first page load (use_titles not set), default to all preferred titles active.
    # Once the user interacts with the form, use_titles=1 is always sent,
    # so we use whatever titles are checked (even if none).
    active_titles = titles if use_titles else preferred_titles

    conditions = ["(date_posted >= date('now', '-90 days') OR (date_posted IS NULL AND created_at >= date('now', '-90 days')))"]
    params = []

    if q:
        conditions.append("(title LIKE ? OR company LIKE ? OR tags LIKE ?)")
        params.extend([f"%{q}%", f"%{q}%", f"%{q}%"])

    if active_titles:
        title_conditions = " OR ".join(["title LIKE ?" for _ in active_titles])
        conditions.append(f"({title_conditions})")
        params.extend([f"%{t}%" for t in active_titles])

    if location:
        conditions.append("location LIKE ?")
        params.append(f"%{location}%")

    if remote:
        conditions.append("(LOWER(location) LIKE '%remote%' OR LOWER(tags) LIKE '%remote%')")

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    query = f"""
        SELECT *,
            CASE WHEN (
                date_posted >= date('now', '-2 days')
                OR (date_posted IS NULL AND created_at >= date('now', '-2 days'))
            ) THEN 1 ELSE 0 END as is_new
        FROM jobs {where} ORDER BY created_at DESC LIMIT 100
    """

    jobs = conn.execute(query, params).fetchall()

    # Fetch saved job IDs so the template can show "✓ Saved" on already-saved jobs
    saved = conn.execute("SELECT job_id FROM saved_jobs").fetchall()
    saved_ids = {row["job_id"] for row in saved}

    conn.close()

    return templates.TemplateResponse("jobs.html", {
        "request": request,
        "jobs": jobs,
        "q": q,
        "location": location,
        "remote": remote,
        "active_titles": active_titles,
        "preferred_titles": preferred_titles,
        "saved_ids": saved_ids,
    })
                                                                         
                                                                                                                                 
@router.post("/jobs/fetch")                                                                                                    
def trigger_fetch():                                                                                                           
    # Run the scraper fetch in the background so the request returns immediately                                               
    # rather than making the browser wait 30-60 seconds for all scrapers to finish.
    import threading
    thread = threading.Thread(target=fetch_all_jobs)
    thread.daemon = True  # thread won't block the app from shutting down
    thread.start()
    return {"message": "Fetch started"}