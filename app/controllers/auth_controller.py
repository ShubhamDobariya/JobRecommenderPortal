from app.schemas.user_schema import UserCreate, UserLogin
from app.core.db import users_collection
from app.core.security import hash_password, verify_password, create_access_token
from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timezone
from typing import Dict


async def signup_user(user_data: UserCreate) -> Dict:
    """
    Registers a new user after checking if email is unique.
    Password is hashed before saving.
    """
    existing_user = await users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    hashed_pwd = hash_password(user_data.password)
    new_user = {
        "username": user_data.username,
        "email": user_data.email,
        "password": hashed_pwd,
        "created_at": datetime.now(timezone.utc),
    }

    try:
        result = await users_collection.insert_one(new_user)
        return {
            "success": True,
            "msg": "User registered successfully",
            "user_id": str(result.inserted_id),
        }
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
        )


async def login_user(user_data: UserLogin) -> Dict:
    """
    Verifies user credentials and returns success status with user info.
    """
    user = await users_collection.find_one({"email": user_data.email})
    if not user:
        return {"success": False, "message": "Invalid email or password"}

    if not verify_password(user_data.password, user["password"]):
        return {"success": False, "message": "Invalid email or password"}

    token = create_access_token(
        data={"user_id": str(user["_id"]), "email": user["email"]}
    )

    return {
        "success": True,
        "user_id": str(user["_id"]),
        "access_token": token,
        "token_type": "bearer",
        "user": {"username": user["username"], "email": user["email"]},
    }
