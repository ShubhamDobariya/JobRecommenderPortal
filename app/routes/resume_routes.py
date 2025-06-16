from fastapi import APIRouter, Request, HTTPException, Request, UploadFile, File
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import cloudinary.uploader
from docx import Document
import PyPDF2
from app.core.cloudinaryConfig import (
    resumes_collection,
    configure_cloudinary,
    get_cloudinary_upload_params,
)

# import os
# import re
# from typing import Dict, List
# import io

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
    text = ""

    if resume.filename.endswith(".pdf"):
        # PDF extraction
        pdf = PyPDF2.PdfReader(resume.file)
        for page in pdf.pages:
            text += page.extract_text()
    elif resume.filename.endswith(".docx"):
        # DOCX extraction
        doc = Document(resume.file)
        for para in doc.paragraphs:
            text += para.text

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


# job portal route
@router.get("/Job-Portal")
async def get_jobs_portal(request: Request):
    user_id = request.session.get("user")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)

    return templates.TemplateResponse(
        "jobPortal.html", {"request": request, "user_id": user_id}
    )
