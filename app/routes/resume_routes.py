from fastapi import APIRouter, Request, Request, UploadFile, File
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import cloudinary.uploader
from app.core.cloudinaryConfig import (
    resumes_collection,
    configure_cloudinary,
    get_cloudinary_upload_params,
)
from app.controllers.resume_parser import extract_text_from_resume
from app.controllers.job_controller import recommend_jobs

# import os
# import re
# from typing import Dict, List
# import io
# from docx import Document
# import PyPDF2 (Remove from my venv)

router = APIRouter(tags=["Resume Upload"])
templates = Jinja2Templates(directory="app/templates")

# Initialize Cloudinary
cloudinary = configure_cloudinary()


@router.get("/Upload-Resume")
async def get_uploadResume(request: Request):
    user_id = request.session.get("user")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)

    return templates.TemplateResponse("uploadResume.html", {"request": request})


@router.post("/Upload-Resume")
async def uploadResume(request: Request, resume: UploadFile = File(...)):

    # Check if the user is authenticated
    user_id = request.session.get("user")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)

    # File validation
    allowed = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]

    if resume.content_type not in allowed:
        return JSONResponse({"error": "Invalid file format"}, status_code=400)

    if resume.file._file.tell() > 5 * 1024 * 1024:
        return JSONResponse(
            {"error": "File size exceeds maximum limit"}, status_code=400
        )

    resume.file.seek(0)

    # Cloudinary upload
    try:
        upload_params = get_cloudinary_upload_params(
            user_id=user_id, filename=resume.filename
        )
        result = cloudinary.uploader.upload(resume.file, **upload_params)
    except Exception as e:
        return JSONResponse(
            {"error": f"Cloudinary upload failed: {str(e)}"}, status_code=500
        )

    # Extract text from the document
    text = extract_text_from_resume(resume)

    # Store in your database
    resumes_collection.insert_one(
        {
            "user_id": user_id,
            "file_name": f"{user_id}_{resume.filename}",
            "file_url": result["secure_url"],
            "text": text,
        }
    )

    return RedirectResponse(url="/Job-Portal", status_code=302)


@router.get("/Job-Portal")
async def get_jobs_portal(request: Request):
    user_id = request.session.get("user")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)

    # Fetch resume from DB
    resume = await resumes_collection.find_one({"user_id": user_id})
    if not resume or "text" not in resume:
        return RedirectResponse(url="/Upload-Resume")

    # Extract text and recommend jobs
    resume_text = resume["text"]
    recommended_jobs = recommend_jobs(resume_text, top_n=5)
    print("recommended_jobs", recommended_jobs)

    # Render recommended jobs in portal
    return templates.TemplateResponse(
        "jobPortal.html",
        {"request": request, "user_id": user_id, "jobs": recommended_jobs},
    )
