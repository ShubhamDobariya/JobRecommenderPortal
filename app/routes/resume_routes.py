from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates


router = APIRouter(tags=["Resume Upload"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/Upload-Resume")
async def uploadResume(request: Request):
    user_id = request.session.get("user")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("uploadResume.html", {"request": request})
