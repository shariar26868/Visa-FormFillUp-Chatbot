"""
MongoDB Database Connection
"""

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

mongodb = MongoDB()

async def connect_to_mongodb():
    mongodb.client = AsyncIOMotorClient(settings.MONGODB_URI)
    mongodb.db = mongodb.client[settings.MONGODB_DB_NAME]
    print(f"✅ MongoDB Connected: {settings.MONGODB_DB_NAME}")

async def close_mongodb_connection():
    if mongodb.client:
        mongodb.client.close()
        print("❌ MongoDB Disconnected")

def get_database():
    return mongodb.db

def get_forms_collection():
    return mongodb.db.forms

def get_conversations_collection():
    return mongodb.db.conversations

def get_pdf_documents_collection():
    return mongodb.db.pdf_documents

def get_summaries_collection():
    return mongodb.db.summaries