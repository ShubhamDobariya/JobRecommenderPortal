from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.schemas.user_schema import UserCreate, UserLogin
from app.controllers.auth_controller import signup_user, login_user

router = APIRouter(tags=["Authentication"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/signup", response_class=HTMLResponse)
async def get_signup(request: Request):
    if request.session.get("user"):
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("signup.html", {"request": request})


@router.post("/signup")
async def register(user: UserCreate, request: Request):
    result = await signup_user(user)
    request.session["user"] = result.get("user_id")  # store session
    return RedirectResponse(url="/dashboard", status_code=302)


@router.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    if request.session.get("user"):
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(user: UserLogin, request: Request):
    result = await login_user(user)
    if result.get("success"):
        request.session["user"] = result.get("user_id")
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse(
        "login.html", {"request": request, "error": result.get("message")}
    )
