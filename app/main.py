from app.database import init_db
from fastapi import FastAPI, Request                                    
from fastapi.staticfiles import StaticFiles                             
from fastapi.templating import Jinja2Templates

app = FastAPI(title="JobLens")
@app.on_event("startup")
def startup():
    init_db()
app.mount("/static", StaticFiles(directory="static"), name="static")

from app.routes.jobs import router as jobs_router
app.include_router(jobs_router) 

templates = Jinja2Templates(directory="app/templates")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})
