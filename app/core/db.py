from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import MONGODB_URI, DATABASE_NAME

client = AsyncIOMotorClient(MONGODB_URI)
db = client[DATABASE_NAME]
