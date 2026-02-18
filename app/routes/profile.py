from fastapi import APIRouter, Request, Form                                                                                                         
from fastapi.templating import Jinja2Templates                                                                                                       
from fastapi.responses import RedirectResponse                                                                                                       
from app.database import get_db
                                                                                                                                                    
router = APIRouter()                                                                                                                                 
templates = Jinja2Templates(directory="app/templates")


@router.get("/profile")
def show_profile(request: Request):
    conn = get_db()

    # We only ever have one profile (your own), so LIMIT 1 is intentional.
    # fetchone() returns a single row, or None if the table is empty.
    profile = conn.execute("SELECT * FROM profiles LIMIT 1").fetchone()
    conn.close()

    # Pass the profile to the template. If it's None (first visit),
    # the template will render an empty form.
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "profile": profile,
    })


@router.post("/profile")
def save_profile(
    request: Request,
    # Form(...) tells FastAPI to read each of these values from the
    # submitted HTML form, matched by the input's name attribute.
    # The default value (e.g. "") is used if the field is left blank.
    name: str = Form(""),
    email: str = Form(""),
    current_title: str = Form(""),
    years_experience: int = Form(0),
    skills: str = Form(""),
    education: str = Form(""),
    languages: str = Form(""),
    location_preference: str = Form(""),
    open_to_remote: bool = Form(False),
    bio: str = Form(""),
):
    conn = get_db()

    # Check if a profile row already exists before deciding INSERT vs UPDATE.
    # We only need the id here, not the full row.
    existing = conn.execute("SELECT id FROM profiles LIMIT 1").fetchone()

    if existing:
        # Profile already exists — update it in place rather than creating a duplicate.
        # updated_at is set to now so we can see when it was last changed.
        conn.execute("""
            UPDATE profiles SET
                name=?, email=?, current_title=?, years_experience=?,
                skills=?, education=?, languages=?, location_preference=?,
                open_to_remote=?, bio=?,
                updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """, (name, email, current_title, years_experience, skills, education,
            languages, location_preference, open_to_remote, bio, existing["id"]))
    else:
        # First time saving — insert a fresh row.
        conn.execute("""
            INSERT INTO profiles
                (name, email, current_title, years_experience, skills, education,
                languages, location_preference, open_to_remote, bio)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, email, current_title, years_experience, skills, education,
            languages, location_preference, open_to_remote, bio))

    conn.commit()
    conn.close()

    # 303 See Other is the correct HTTP status for redirecting after a form POST.
    # It tells the browser to follow the redirect with a GET request,
    # which prevents the "resubmit form?" warning if the user refreshes.
    return RedirectResponse(url="/profile", status_code=303)