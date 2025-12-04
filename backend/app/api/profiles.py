from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import pandas as pd
import io
from app.database import get_db
from app.models.profile import Profile
from app.models.connection import Connection
from app.services.linkedin import linkedin_service
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


class ScrapeSearchRequest(BaseModel):
    search_url: str
    max_results: int = 50


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
    # Priority order: exact matches first, then partial matches
    url_col = None
    name_col = None
    company_col = None
    title_col = None
    notes_col = None
    tags_col = None

    for col in df.columns:
        col_lower = col.lower()
        # LinkedIn URL - prioritize linkedinProfileUrl, linkedinProfileUrl, etc.
        if not url_col:
            if 'linkedinprofileurl' in col_lower or 'linkedinurl' in col_lower:
                url_col = col
            elif ('url' in col_lower or 'linkedin' in col_lower) and 'profile' in col_lower:
                url_col = col
            elif 'url' in col_lower and 'linkedin' in col_lower:
                url_col = col
        
        # Name - prioritize fullName, full name, etc.
        if not name_col:
            if 'fullname' in col_lower or 'full name' in col_lower:
                name_col = col
            elif 'name' in col_lower and 'first' not in col_lower and 'last' not in col_lower:
                name_col = col
        
        # Company - prioritize companyName, company name, etc.
        if not company_col:
            if 'companyname' in col_lower or 'company name' in col_lower:
                company_col = col
            elif 'company' in col_lower and 'url' not in col_lower and 'slug' not in col_lower:
                company_col = col
            elif 'organization' in col_lower:
                company_col = col
        
        # Title - prioritize linkedinJobTitle, job title, etc.
        if not title_col:
            if 'linkedinjobtitle' in col_lower or 'jobtitle' in col_lower:
                title_col = col
            elif 'title' in col_lower and 'job' in col_lower:
                title_col = col
            elif 'title' in col_lower or 'position' in col_lower or 'role' in col_lower:
                title_col = col
        
        # Notes - can use description or headline
        if not notes_col:
            if 'note' in col_lower or 'comment' in col_lower:
                notes_col = col
            elif 'description' in col_lower and 'job' not in col_lower:
                notes_col = col
            elif 'headline' in col_lower:
                notes_col = col
        
        # Tags - skills or tags
        if not tags_col:
            if 'tag' in col_lower:
                tags_col = col
            elif 'skill' in col_lower:
                tags_col = col

    if not url_col:
        raise HTTPException(status_code=400, detail="CSV must contain a LinkedIn URL column")

    profiles_created = 0
    errors = []

    for idx, row in df.iterrows():
        try:
            # Get URL value and validate
            url_value = row[url_col] if url_col else None
            if pd.isna(url_value) or not url_value:
                errors.append(f"Row {idx + 1}: Missing LinkedIn URL")
                continue

            linkedin_url = str(url_value).strip()
            if not linkedin_url or linkedin_url.lower() in ['nan', 'none', 'null', '']:
                errors.append(f"Row {idx + 1}: Invalid LinkedIn URL")
                continue

            # Ensure URL format
            if not linkedin_url.startswith('http'):
                # Extract username from URL if it's just a username
                username = linkedin_url.replace('linkedin.com/in/', '').replace('www.linkedin.com/in/', '').strip('/')
                linkedin_url = f"https://www.linkedin.com/in/{username}"

            # Validate URL length (database constraint)
            if len(linkedin_url) > 500:  # Reasonable max length
                errors.append(f"Row {idx + 1}: URL too long")
                continue

            # Check if profile already exists
            existing = db.query(Profile).filter(Profile.linkedin_url == linkedin_url).first()
            if existing:
                continue  # Skip duplicates silently

            # Get name with proper handling
            name_value = row[name_col] if name_col else None
            if pd.isna(name_value) or not name_value:
                name = "Unknown"
            else:
                name = str(name_value).strip()
                if not name or name.lower() in ['nan', 'none', 'null']:
                    name = "Unknown"

            # Get optional fields with proper null handling
            def safe_str(col_name):
                if not col_name:
                    return None
                val = row.get(col_name)
                if pd.isna(val) or not val:
                    return None
                str_val = str(val).strip()
                return str_val if str_val and str_val.lower() not in ['nan', 'none', 'null', ''] else None

            profile = Profile(
                linkedin_url=linkedin_url,
                name=name,
                company=safe_str(company_col),
                title=safe_str(title_col),
                notes=safe_str(notes_col),
                tags=safe_str(tags_col),
            )
            db.add(profile)
            profiles_created += 1
            
            # Commit in batches to avoid large transactions
            if profiles_created % 50 == 0:
                db.commit()
        except Exception as e:
            errors.append(f"Row {idx + 1}: {str(e)}")
            db.rollback()  # Rollback on error to avoid partial commits
            continue

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        errors.append(f"Database error during commit: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save profiles: {str(e)}")

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


@router.post("/scrape")
async def scrape_linkedin_search(
    request: ScrapeSearchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Scrape LinkedIn search results and create profiles"""
    # Validate URL
    if not request.search_url or 'linkedin.com/search' not in request.search_url:
        raise HTTPException(status_code=400, detail="Invalid LinkedIn search URL")
    
    if request.max_results < 1 or request.max_results > 100:
        raise HTTPException(status_code=400, detail="max_results must be between 1 and 100")
    
    try:
        # Scrape profiles from search results
        scraped_profiles = await linkedin_service.scrape_search_results(
            request.search_url,
            max_results=request.max_results
        )
        
        if not scraped_profiles:
            return {
                "message": "No profiles found in search results",
                "profiles_created": 0,
                "errors": []
            }
        
        profiles_created = 0
        errors = []
        
        for profile_data in scraped_profiles:
            try:
                linkedin_url = profile_data.get('linkedin_url')
                if not linkedin_url:
                    continue
                
                # Normalize URL
                if not linkedin_url.startswith('http'):
                    linkedin_url = f"https://www.linkedin.com{linkedin_url}"
                
                # Check if profile already exists
                existing = db.query(Profile).filter(Profile.linkedin_url == linkedin_url).first()
                if existing:
                    continue
                
                # Create new profile
                profile = Profile(
                    linkedin_url=linkedin_url,
                    name=profile_data.get('name', 'Unknown'),
                    company=profile_data.get('company'),
                    title=profile_data.get('title'),
                )
                db.add(profile)
                profiles_created += 1
                
            except Exception as e:
                errors.append(f"Error creating profile {profile_data.get('name', 'Unknown')}: {str(e)}")
                continue
        
        db.commit()
        
        return {
            "message": f"Successfully scraped and imported {profiles_created} profiles",
            "profiles_created": profiles_created,
            "errors": errors
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error scraping LinkedIn search: {str(e)}")




