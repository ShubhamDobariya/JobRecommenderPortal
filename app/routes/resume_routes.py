from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import cloudinary.uploader
from app.core.cloudinaryConfig import (
    resumes_collection,
    configure_cloudinary,
    get_cloudinary_upload_params,
)
from app.controllers.resume_parser import extract_text_from_resume_file
from app.controllers.job_controller import recommend_jobs

# import os
# import re
# from typing import Dict, List
# import io
# from docx import Document
# import PyPDF2 (Remove from my venv)

router = APIRouter(tags=["Resume Upload"])
templates = Jinja2Templates(directory="app/templates")

cloudinary = configure_cloudinary()

job_cache = {}
job_details_cache = {}


@router.get("/Upload-Resume")
async def get_uploadResume(request: Request):
    user_id = request.session.get("user")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)

    existing_resume = await resumes_collection.find_one({"user_id": user_id})
    allow_update = request.session.get("allow_resume_update")

    if existing_resume and not allow_update:
        return RedirectResponse(url="/Job-Portal", status_code=302)

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

    # Get file size properly
    resume.file.seek(0, 2)  # Seek to end
    file_size = resume.file.tell()
    resume.file.seek(0)  # Reset to beginning

    if file_size > 5 * 1024 * 1024:
        return JSONResponse(
            {"error": "File size exceeds maximum limit"}, status_code=400
        )

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

    text = extract_text_from_resume_file(resume)

    if not text:
        text = "No text could be extracted from the resume"

    # Store resume data in database (delete existing resume first)
    try:
        await resumes_collection.delete_many({"user_id": user_id})

        ext = resume.filename.split(".")[-1].lower()
        stored_filename = (
            f"resume_{user_id}.{ext}" if ext in ["pdf", "docx"] else f"resume_{user_id}"
        )
        await resumes_collection.insert_one(
            {
                "user_id": user_id,
                "file_name": stored_filename,
                "file_url": result["secure_url"],
                "text": text,
            }
        )
    except Exception as e:
        return JSONResponse({"error": f"Database error: {str(e)}"}, status_code=500)

    request.session.pop("allow_resume_update", None)

    # Store in global cache
    job_cache[user_id] = await recommend_jobs(text)

    return RedirectResponse(url="/Job-Portal", status_code=302)


@router.get("/Job-Portal")
async def get_jobs_portal(request: Request):
    user_id = request.session.get("user")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)

    # Fetch resume from DB
    try:
        # Use cached jobs if available
        if user_id in job_cache:
            return templates.TemplateResponse(
                "jobPortal.html",
                {"request": request, "user_id": user_id, "jobs": job_cache[user_id]},
            )
        resume = await resumes_collection.find_one({"user_id": user_id})
        if not resume:
            print(f"No resume found for user_id: {user_id}")
            return RedirectResponse(url="/Upload-Resume", status_code=302)

        if "text" not in resume or not resume["text"]:
            print(f"No text found in resume for user_id: {user_id}")
            return RedirectResponse(url="/Upload-Resume", status_code=302)

        resume_text = resume["text"]
        print(f"Resume text length: {len(resume_text)}")

        recommended_jobs = await recommend_jobs(resume_text, top_n=10)
        print("recommended_jobs", recommended_jobs)

        job_cache[user_id] = recommended_jobs
        job_details_cache[user_id] = {
            str(i + 1): job for i, job in enumerate(recommended_jobs)
        }
        print("job details", job_details_cache)

        # Render recommended jobs in portal
        return templates.TemplateResponse(
            "jobPortal.html",
            {"request": request, "user_id": user_id, "jobs": recommended_jobs},
        )
    except Exception as e:
        print(f"Error in get_jobs_portal: {e}")
        return RedirectResponse(url="/Upload-Resume", status_code=302)


@router.get("/request-resume-update")
async def request_resume_update(request: Request):
    user_id = request.session.get("user")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)

    # Clear cached jobs
    job_cache.pop(user_id, None)

    request.session["allow_resume_update"] = True
    return RedirectResponse(url="/Upload-Resume", status_code=302)


@router.get("/job-{job_id}")
async def job_detail(request: Request, job_id: str):
    user_id = request.session.get("user")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)

    job = job_details_cache.get(user_id, {}).get(job_id)
    if not job:
        return RedirectResponse(url="/Job-Portal", status_code=302)

    return templates.TemplateResponse(
        "jobDetail.html", {"request": request, "job": job}
    )
