from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api import profiles, connections, messages, stats
from app.services.scheduler import start_scheduler

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="LinkedIn Prospection Agent API", version="1.0.0")

# CORS middleware
from app.config import settings

# Parse allowed origins from environment variable
# When allow_credentials=True, we cannot use ["*"], so we need explicit origins
if settings.allowed_origins == "*":
    # Default to allowing common origins for development
    # In production, set ALLOWED_ORIGINS explicitly
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://linkedin-prospection-agent-byydlem7b-chyll.vercel.app",
        "https://linkedin-prospection-agent-*.vercel.app",  # Pattern for preview deployments
    ]
else:
    # Parse comma-separated origins
    allowed_origins = [origin.strip() for origin in settings.allowed_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(profiles.router, prefix="/api/profiles", tags=["profiles"])
app.include_router(connections.router, prefix="/api/connections", tags=["connections"])
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])


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


