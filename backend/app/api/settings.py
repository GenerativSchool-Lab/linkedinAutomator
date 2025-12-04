from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.settings import AppSettings
from pydantic import BaseModel


router = APIRouter()


class SettingsResponse(BaseModel):
    company_name: str | None
    company_description: str | None
    value_proposition: str | None

    class Config:
        from_attributes = True


class SettingsUpdateRequest(BaseModel):
    company_name: str | None = None
    company_description: str | None = None
    value_proposition: str | None = None


@router.get("", response_model=SettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    """Get current app settings"""
    settings = db.query(AppSettings).filter(AppSettings.id == 1).first()
    if not settings:
        # Create default settings if they don't exist
        settings = AppSettings(id=1)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return SettingsResponse(
        company_name=settings.company_name,
        company_description=settings.company_description,
        value_proposition=settings.value_proposition
    )


@router.put("", response_model=SettingsResponse)
def update_settings(request: SettingsUpdateRequest, db: Session = Depends(get_db)):
    """Update app settings"""
    settings = db.query(AppSettings).filter(AppSettings.id == 1).first()
    
    if not settings:
        settings = AppSettings(id=1)
        db.add(settings)
    
    if request.company_name is not None:
        settings.company_name = request.company_name
    if request.company_description is not None:
        settings.company_description = request.company_description
    if request.value_proposition is not None:
        settings.value_proposition = request.value_proposition
    
    db.commit()
    db.refresh(settings)
    
    return SettingsResponse(
        company_name=settings.company_name,
        company_description=settings.company_description,
        value_proposition=settings.value_proposition
    )

