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

    return {
        "resource_type": "raw",
        "folder": f"resumes/{user_id}_{filename}",
        "public_id": f"{user_id}_{filename}",
        "use_filename": True,
        "unique_filename": False,
        "overwrite": False,
    }
