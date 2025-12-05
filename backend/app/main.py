from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api import profiles, connections, messages, stats
from app.api import settings as settings_api
from app.services.scheduler import start_scheduler
# Import models to ensure they're registered with SQLAlchemy
from app.models import Profile, Connection, Message, FollowUp, AppSettings

# Run Alembic migrations on startup
from alembic.config import Config
from alembic import command

def run_migrations():
    """Run Alembic migrations"""
    import os
    from sqlalchemy import inspect, text
    
    try:
        # Check if alembic_version table exists
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        # If tables exist but alembic_version doesn't, we need to stamp the database
        if 'profiles' in tables and 'alembic_version' not in tables:
            print("Database tables exist but alembic_version table is missing. Stamping database...")
            # Get the path to alembic.ini
            alembic_ini_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "alembic.ini")
            if not os.path.exists(alembic_ini_path):
                alembic_ini_path = "alembic.ini"
            
            alembic_cfg = Config(alembic_ini_path)
            # Check if failure_reason column exists
            if 'connections' in tables:
                columns = [col['name'] for col in inspector.get_columns('connections')]
                if 'failure_reason' in columns:
                    # All migrations are applied, stamp as head
                    command.stamp(alembic_cfg, "head")
                    print("Stamped database as head (all migrations already applied)")
                else:
                    # Stamp as initial, then run the failure_reason migration
                    command.stamp(alembic_cfg, "001_initial")
                    command.upgrade(alembic_cfg, "head")
                    print("Stamped database as 001_initial and ran remaining migrations")
            else:
                # No connections table, stamp as initial
                command.stamp(alembic_cfg, "001_initial")
                print("Stamped database as 001_initial")
        elif 'alembic_version' in tables:
            # Normal migration path
            alembic_ini_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "alembic.ini")
            if not os.path.exists(alembic_ini_path):
                alembic_ini_path = "alembic.ini"
            
            alembic_cfg = Config(alembic_ini_path)
            command.upgrade(alembic_cfg, "head")
            print("Database migrations completed successfully")
        else:
            # No tables exist, run migrations normally
            alembic_ini_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "alembic.ini")
            if not os.path.exists(alembic_ini_path):
                alembic_ini_path = "alembic.ini"
            
            alembic_cfg = Config(alembic_ini_path)
            command.upgrade(alembic_cfg, "head")
            print("Database migrations completed successfully")
    except Exception as e:
        print(f"Warning: Could not run migrations: {e}")
        import traceback
        traceback.print_exc()
        # Fallback: ensure tables exist using create_all (won't recreate existing tables)
        try:
            Base.metadata.create_all(bind=engine)
            print("Fallback: Ensured tables exist using create_all")
        except Exception as e2:
            print(f"Error: Could not ensure tables exist: {e2}")

# Run migrations on startup
run_migrations()

app = FastAPI(title="LinkedIn Prospection Agent API", version="1.0.0")

# CORS middleware
from app.config import settings
import os
import re

# Parse allowed origins from environment variable
# When allow_credentials=True, we cannot use ["*"], so we need explicit origins
if settings.allowed_origins == "*":
    # Default to allowing common origins for development and production
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://linkedin-prospection-agent.vercel.app",  # Production URL
        "https://linkedin-prospection-agent-djy5zdbv9-chyll.vercel.app",
        "https://linkedin-prospection-agent-cw0glxlj7-chyll.vercel.app",
        "https://linkedin-prospection-agent-eituic75a-chyll.vercel.app",
        "https://linkedin-prospection-agent-mukocvm6p-chyll.vercel.app",
        "https://linkedin-prospection-agent-pwjhey86b-chyll.vercel.app",
        "https://linkedin-prospection-agent-hr285ngf4-chyll.vercel.app",
    ]
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

# Use a more permissive approach: allow all Vercel URLs via regex
# This allows both production and preview deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://linkedin-prospection-agent(-[a-z0-9]+)?\.vercel\.app",  # Allow all Vercel URLs for this project (production and preview)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(profiles.router, prefix="/api/profiles", tags=["profiles"])
app.include_router(connections.router, prefix="/api/connections", tags=["connections"])
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
app.include_router(settings_api.router, prefix="/api/settings", tags=["settings"])


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


