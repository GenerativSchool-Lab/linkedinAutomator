from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import pandas as pd
import io
from app.database import get_db
from app.models.profile import Profile
from app.models.connection import Connection
from pydantic import BaseModel

router = APIRouter()


class ProfileResponse(BaseModel):
    id: int
    name: str
    linkedin_url: str
    company: Optional[str]
    title: Optional[str]
    notes: Optional[str]
    tags: Optional[str]
    created_at: str
    connection_status: Optional[str] = None

    class Config:
        from_attributes = True


@router.post("/upload")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload and parse CSV file"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    contents = await file.read()
    try:
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing CSV: {str(e)}")

    # Try to identify columns (flexible mapping)
    url_col = None
    name_col = None
    company_col = None
    title_col = None
    notes_col = None
    tags_col = None

    for col in df.columns:
        col_lower = col.lower()
        if 'url' in col_lower or 'linkedin' in col_lower or 'profile' in col_lower:
            url_col = col
        elif 'name' in col_lower or 'full name' in col_lower:
            name_col = col
        elif 'company' in col_lower or 'organization' in col_lower:
            company_col = col
        elif 'title' in col_lower or 'position' in col_lower or 'role' in col_lower:
            title_col = col
        elif 'note' in col_lower or 'comment' in col_lower:
            notes_col = col
        elif 'tag' in col_lower:
            tags_col = col

    if not url_col:
        raise HTTPException(status_code=400, detail="CSV must contain a LinkedIn URL column")

    profiles_created = 0
    errors = []

    for idx, row in df.iterrows():
        try:
            linkedin_url = str(row[url_col]).strip()
            if not linkedin_url or linkedin_url == 'nan':
                continue

            # Ensure URL format
            if not linkedin_url.startswith('http'):
                linkedin_url = f"https://www.linkedin.com/in/{linkedin_url.replace('linkedin.com/in/', '').strip('/')}"

            # Check if profile already exists
            existing = db.query(Profile).filter(Profile.linkedin_url == linkedin_url).first()
            if existing:
                continue

            profile = Profile(
                linkedin_url=linkedin_url,
                name=str(row[name_col]).strip() if name_col and pd.notna(row.get(name_col)) else "Unknown",
                company=str(row[company_col]).strip() if company_col and pd.notna(row.get(company_col)) else None,
                title=str(row[title_col]).strip() if title_col and pd.notna(row.get(title_col)) else None,
                notes=str(row[notes_col]).strip() if notes_col and pd.notna(row.get(notes_col)) else None,
                tags=str(row[tags_col]).strip() if tags_col and pd.notna(row.get(tags_col)) else None,
            )
            db.add(profile)
            profiles_created += 1
        except Exception as e:
            errors.append(f"Row {idx + 1}: {str(e)}")

    db.commit()

    return {
        "message": f"Successfully imported {profiles_created} profiles",
        "profiles_created": profiles_created,
        "errors": errors
    }


@router.get("", response_model=List[ProfileResponse])
def get_profiles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get list of profiles with optional filters"""
    query = db.query(Profile)

    # Filter by company
    if company:
        query = query.filter(Profile.company.ilike(f"%{company}%"))

    # Filter by connection status
    if status:
        query = query.join(Connection).filter(Connection.status == status)

    profiles = query.offset(skip).limit(limit).all()

    result = []
    for profile in profiles:
        # Get latest connection status
        connection = db.query(Connection).filter(Connection.profile_id == profile.id).order_by(Connection.created_at.desc()).first()
        profile_data = ProfileResponse(
            id=profile.id,
            name=profile.name,
            linkedin_url=profile.linkedin_url,
            company=profile.company,
            title=profile.title,
            notes=profile.notes,
            tags=profile.tags,
            created_at=profile.created_at.isoformat() if profile.created_at else None,
            connection_status=connection.status.value if connection else None
        )
        result.append(profile_data)

    return result


@router.get("/{profile_id}", response_model=ProfileResponse)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    """Get a single profile by ID"""
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    connection = db.query(Connection).filter(Connection.profile_id == profile.id).order_by(Connection.created_at.desc()).first()
    
    return ProfileResponse(
        id=profile.id,
        name=profile.name,
        linkedin_url=profile.linkedin_url,
        company=profile.company,
        title=profile.title,
        notes=profile.notes,
        tags=profile.tags,
        created_at=profile.created_at.isoformat() if profile.created_at else None,
        connection_status=connection.status.value if connection else None
    )




