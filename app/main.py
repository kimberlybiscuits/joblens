from app.database import init_db                                                                                                           
from app.scheduler import scheduler                                                                                                        
from fastapi import FastAPI, Request                                                                                                       
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates                                                                                             
                                                                                                                                            
app = FastAPI(title="JobLens")

# on_event("startup") runs once when uvicorn starts the app.
# Good place to initialise anything the app needs before serving requests.
@app.on_event("startup")
def startup():
    init_db()
    scheduler.start()  # begin background scraping schedule

# on_event("shutdown") runs when uvicorn is stopped (e.g. Ctrl+C).
# Lets us clean up gracefully rather than leaving threads hanging.
@app.on_event("shutdown")
def shutdown():
    scheduler.shutdown()

# Serve files from the /static directory (CSS, JS, images etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

from app.routes.jobs import router as jobs_router
app.include_router(jobs_router)

from app.routes.profile import router as profile_router                                                                                              
app.include_router(profile_router)   

from app.routes.saved import router as saved_router                                                                                                   
app.include_router(saved_router)   


templates = Jinja2Templates(directory="app/templates")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})