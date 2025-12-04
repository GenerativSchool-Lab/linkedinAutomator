from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api import profiles, connections, messages, stats, settings
from app.services.scheduler import start_scheduler
# Import models to ensure they're registered with SQLAlchemy
from app.models import Profile, Connection, Message, FollowUp, AppSettings

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="LinkedIn Prospection Agent API", version="1.0.0")

# CORS middleware
from app.config import settings
import os
import re

# Parse allowed origins from environment variable
# When allow_credentials=True, we cannot use ["*"], so we need explicit origins
if settings.allowed_origins == "*":
    # Default to allowing common origins for development
    # In production, set ALLOWED_ORIGINS explicitly via environment variable
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]
    # Add Vercel URLs - we'll use a regex pattern for dynamic matching
    # But since FastAPI doesn't support regex directly, we'll add common patterns
    # For production, set ALLOWED_ORIGINS env var with your specific Vercel URL
    vercel_base = os.getenv("VERCEL_URL") or "linkedin-prospection-agent"
    if vercel_base and not vercel_base.startswith("http"):
        # Add common Vercel URL patterns
        allowed_origins.extend([
            f"https://{vercel_base}.vercel.app",
            f"https://{vercel_base}-*.vercel.app",
        ])
else:
    # Parse comma-separated origins
    allowed_origins = [origin.strip() for origin in settings.allowed_origins.split(",")]

# Custom origin validator for Vercel URLs
def is_origin_allowed(origin: str) -> bool:
    """Check if origin is allowed, including Vercel preview URLs"""
    if not origin:
        return False
    
    # Check exact matches
    if origin in allowed_origins:
        return True
    
    # Allow localhost for development
    if origin.startswith("http://localhost"):
        return True
    
    # Allow Vercel preview URLs (pattern: *.vercel.app)
    if re.match(r"^https://[a-z0-9-]+\.vercel\.app$", origin):
        return True
    
    return False

# Use a more permissive approach: allow all origins but validate in middleware
# Since FastAPI CORS doesn't support dynamic validation easily, we'll use allow_origin_regex
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",  # Allow all Vercel preview URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(profiles.router, prefix="/api/profiles", tags=["profiles"])
app.include_router(connections.router, prefix="/api/connections", tags=["connections"])
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])


@app.on_event("startup")
async def startup_event():
    try:
        start_scheduler()
    except Exception as e:
        print(f"Warning: Could not start scheduler: {e}")
        # Continue even if scheduler fails to start


@app.get("/")
async def root():
    return {"message": "LinkedIn Prospection Agent API"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


