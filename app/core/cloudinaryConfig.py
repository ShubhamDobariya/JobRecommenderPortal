import os
import cloudinary

from dotenv import load_dotenv
from app.core.db import db

# import cloudinary.uploader
# import cloudinary.api

load_dotenv()


def configure_cloudinary():
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True,
    )

    return cloudinary


resumes_collection = db["resumes"]


def get_cloudinary_upload_params(user_id=None, filename=None):
    ext = filename.split(".")[-1].lower() if filename else "pdf"
    return {
        "resource_type": "raw",
        "folder": "resumes",
        "public_id": (
            f"resume_{user_id}.{ext}" if ext in ["pdf", "docx"] else f"resume_{user_id}"
        ),
        "use_filename": False,
        "unique_filename": False,
        "overwrite": True,
    }
