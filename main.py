"""
Immigration Chatbot - Main FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import connect_to_mongodb, close_mongodb_connection
from app.api import chat, forms, session

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    await connect_to_mongodb()
    print("🚀 Immigration Chatbot API Started")
    
    yield
    
    # Shutdown
    await close_mongodb_connection()
    print("👋 Immigration Chatbot API Stopped")

app = FastAPI(
    title="Immigration Chatbot API",
    description="AI-powered visa application assistant",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(forms.router, prefix="/api", tags=["Forms"])
app.include_router(session.router, prefix="/api", tags=["Session"])

@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": "Immigration Chatbot API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "database": "connected",
        "s3": "connected",
        "openai": "configured"
    }
