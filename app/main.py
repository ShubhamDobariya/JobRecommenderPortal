from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.routes.auth_routes import router as auth_router
from app.routes.resume_routes import router as resume_router
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import SECRET_KEY


app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)


# CORS settings (helpful if frontend is on different origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Mount static folder to serve JS, CSS, images etc.
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup Jinja2 templates directory
templates = Jinja2Templates(directory="app/templates")

# Include auth router
app.include_router(auth_router)
app.include_router(resume_router)


@app.get("/")
def read_root(request: Request):
    user_id = request.session.get("user")
    if user_id:
        return RedirectResponse(url="/Upload-Resume", status_code=302)
    return RedirectResponse(url="/login", status_code=302)
