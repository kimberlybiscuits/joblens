from fastapi import APIRouter, Request                                                                                                                
from fastapi.templating import Jinja2Templates                                                                                                        
from fastapi.responses import JSONResponse, HTMLResponse                                                                                                            
from app.database import get_db
                                                                                                                                                    
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post("/jobs/{job_id}/save")
def save_job(job_id: int):
    # Insert the job into saved_jobs. If it's already saved (UNIQUE constraint
    # on job_id), the exception is caught and silently ignored — no duplicates.
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO saved_jobs (job_id) VALUES (?)",
            (job_id,)
        )
        conn.commit()
    except Exception:
        pass  # already saved, nothing to do
    conn.close()
    # Return HTML to replace the button with a static "Saved" confirmation.
    # HTMX will swap this in place of the button (hx-swap="outerHTML" on the button).
    return HTMLResponse('<span class="text-xs text-green-600 border border-green-300 bg-green-50 px-3 py-1 rounded-full">✓ Saved</span>')


@router.post("/jobs/{job_id}/unsave")
def unsave_job(job_id: int):
    # Remove the job from saved_jobs entirely.
    conn = get_db()
    conn.execute("DELETE FROM saved_jobs WHERE job_id = ?", (job_id,))
    conn.commit()
    conn.close()
    # Return empty HTML — HTMX swaps this in place of the card (outerHTML),
    # making it disappear from the page without a reload.
    return HTMLResponse("")


@router.post("/saved/{job_id}/status")
def update_status(job_id: int):
    # Cycles the job's status forward each time it's called.
    # The dict maps current status → next status, looping back to 'saved' at the end.
    cycle = {"saved": "applied", "applied": "heard_back", "heard_back": "saved"}
    conn = get_db()
    current = conn.execute(
        "SELECT status FROM saved_jobs WHERE job_id = ?", (job_id,)
    ).fetchone()
    if current:
        next_status = cycle[current["status"]]
        conn.execute(
            "UPDATE saved_jobs SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE job_id = ?",
            (next_status, job_id)
        )
        conn.commit()
    conn.close()
    return JSONResponse({"status": next_status if current else None})


@router.get("/saved")
def saved_jobs(request: Request):
    # JOIN saved_jobs with jobs to get the full job details alongside the saved
    # status. saved_at is renamed from saved_jobs.created_at to avoid clashing
    # with jobs.created_at.
    conn = get_db()
    jobs = conn.execute("""
        SELECT j.*, s.status, s.created_at as saved_at
        FROM saved_jobs s
        JOIN jobs j ON j.id = s.job_id
        ORDER BY s.created_at DESC
    """).fetchall()
    conn.close()
    return templates.TemplateResponse("saved.html", {
        "request": request,
        "jobs": jobs,
    })