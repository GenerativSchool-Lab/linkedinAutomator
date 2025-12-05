from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db, SessionLocal
from app.models.profile import Profile
from app.models.connection import Connection, ConnectionStatus
from app.models.message import Message, MessageType
from app.services.linkedin import linkedin_service
from app.services.message_generator import message_generator
from app.config import settings
from pydantic import BaseModel
import asyncio

router = APIRouter()


class ConnectionResponse(BaseModel):
    id: int
    profile_id: int
    profile_name: str
    profile_url: str
    status: str
    connected_at: Optional[str]
    created_at: str
    connection_message: Optional[str] = None
    connection_message_sent_at: Optional[str] = None
    failure_reason: Optional[str] = None

    class Config:
        from_attributes = True


class StartConnectionRequest(BaseModel):
    profile_ids: Optional[List[int]] = None  # If None, process all pending profiles


async def process_connection(profile_id: int):
    """Background task to process a single connection"""
    db = SessionLocal()
    try:
        profile = db.query(Profile).filter(Profile.id == profile_id).first()
        if not profile:
            return

        # Check if connection already exists and is connected
        existing = db.query(Connection).filter(Connection.profile_id == profile_id).first()
        if existing and existing.status == ConnectionStatus.CONNECTED:
            # Already connected, no need to retry
            return

        # Create or update connection
        if not existing:
            connection = Connection(
                profile_id=profile_id,
                status=ConnectionStatus.CONNECTING
            )
            db.add(connection)
            db.commit()
            db.refresh(connection)
        else:
            connection = existing
            connection.status = ConnectionStatus.CONNECTING
            db.commit()

        # Scrape profile details for better personalization
        try:
            profile_details = await linkedin_service.scrape_profile_details(profile.linkedin_url)
            # Update profile with scraped details if available
            if profile_details.get('headline') and not profile.title:
                profile.title = profile_details.get('headline')
            if profile_details.get('current_company') and not profile.company:
                profile.company = profile_details.get('current_company')
            if profile_details.get('about') and not profile.notes:
                profile.notes = profile_details.get('about')[:500]  # Limit length
            db.commit()
        except Exception as e:
            print(f"Error scraping profile details: {e}")
            # Continue with existing profile data
        
        # Generate message
        message_content = message_generator.generate_connection_message(profile)

        # Send connection request
        await asyncio.sleep(settings.rate_limit_delay)
        success, status_info = await linkedin_service.send_connection_request(profile.linkedin_url, message_content)

        if success:
            # Create message record
            message = Message(
                connection_id=connection.id,
                content=message_content,
                message_type=MessageType.INITIAL
            )
            db.add(message)
            db.commit()
            db.refresh(message)

            connection.connection_message_id = message.id
            connection.failure_reason = None  # Clear any previous failure reason
            
            # Differentiate between connection sent (PENDING) and already connected (CONNECTED)
            if status_info == "already_connected":
                # Already connected - can send messages
                connection.status = ConnectionStatus.CONNECTED
                connection.connected_at = db.query(Message).filter(Message.id == message.id).first().sent_at
            elif status_info == "pending":
                # Connection request sent, waiting for acceptance
                connection.status = ConnectionStatus.PENDING
                # Don't set connected_at yet - wait for acceptance
            else:
                # Default to PENDING if status unclear
                connection.status = ConnectionStatus.PENDING
        else:
            connection.status = ConnectionStatus.FAILED
            connection.failure_reason = status_info or "Unknown error"

        db.commit()
    except Exception as e:
        print(f"Error processing connection for profile {profile_id}: {e}")
        if 'connection' in locals():
            connection.status = ConnectionStatus.FAILED
            error_msg = str(e)
            # Categorize the error
            if "login" in error_msg.lower():
                connection.failure_reason = "Login/authentication failed"
            elif "timeout" in error_msg.lower():
                connection.failure_reason = "Network timeout"
            elif "profile" in error_msg.lower() and "not found" in error_msg.lower():
                connection.failure_reason = "Profile not found or inaccessible"
            else:
                connection.failure_reason = f"Error: {error_msg[:200]}"  # Limit length
            db.commit()
    finally:
        db.close()


@router.post("/start")
async def start_connections(
    request: StartConnectionRequest,
    db: Session = Depends(get_db)
):
    """Start connection process for profiles"""
    from datetime import datetime, timedelta
    
    if request.profile_ids:
        profiles = db.query(Profile).filter(Profile.id.in_(request.profile_ids)).all()
    else:
        # Get all profiles without connections or with failed connections
        profiles = db.query(Profile).outerjoin(Connection).filter(
            (Connection.id == None) | (Connection.status == ConnectionStatus.FAILED)
        ).all()

    if not profiles:
        return {"message": "No profiles to process"}

    # Check daily limit
    today = datetime.utcnow().date()
    today_connections = db.query(Connection).filter(
        Connection.created_at >= datetime.combine(today, datetime.min.time()),
        Connection.status.in_([ConnectionStatus.CONNECTED, ConnectionStatus.CONNECTING])
    ).count()
    
    if today_connections >= settings.max_connections_per_day:
        return {
            "message": f"Daily limit reached ({settings.max_connections_per_day} connections per day). Please try again tomorrow.",
            "profiles_count": 0,
            "daily_limit_reached": True
        }
    
    # Limit the number of profiles to process based on daily limit
    remaining_slots = settings.max_connections_per_day - today_connections
    profiles_to_process = profiles[:remaining_slots]
    
    if len(profiles) > remaining_slots:
        print(f"Limiting to {remaining_slots} profiles due to daily limit")

    # Process connections sequentially in background to respect rate limits
    async def process_all_connections():
        for profile in profiles_to_process:
            await process_connection(profile.id)
            # Wait between each connection to respect rate limits
            await asyncio.sleep(settings.rate_limit_delay)
    
    # Start processing in background
    asyncio.create_task(process_all_connections())

    return {
        "message": f"Started connection process for {len(profiles_to_process)} profiles (rate limited to {settings.rate_limit_delay}s between requests)",
        "profiles_count": len(profiles_to_process),
        "daily_connections_used": today_connections,
        "daily_connections_remaining": remaining_slots
    }


@router.post("/retry")
async def retry_connections(
    connection_ids: Optional[List[int]] = None,
    db: Session = Depends(get_db)
):
    """Retry failed or pending connections"""
    from datetime import datetime, timedelta
    
    # Get connections to retry
    if connection_ids:
        connections = db.query(Connection).filter(Connection.id.in_(connection_ids)).all()
    else:
        # Retry all failed connections
        connections = db.query(Connection).filter(
            Connection.status == ConnectionStatus.FAILED
        ).all()
    
    if not connections:
        return {"message": "No connections to retry", "retried_count": 0}
    
    # Check daily limit
    today = datetime.utcnow().date()
    today_connections = db.query(Connection).filter(
        Connection.created_at >= datetime.combine(today, datetime.min.time()),
        Connection.status.in_([ConnectionStatus.CONNECTED, ConnectionStatus.CONNECTING, ConnectionStatus.PENDING])
    ).count()
    
    remaining_slots = settings.max_connections_per_day - today_connections
    connections_to_retry = connections[:remaining_slots]
    
    if len(connections) > remaining_slots:
        print(f"Limiting retry to {remaining_slots} connections due to daily limit")
    
    # Process retries sequentially
    async def retry_all_connections():
        for conn in connections_to_retry:
            await process_connection(conn.profile_id)
            await asyncio.sleep(settings.rate_limit_delay)
    
    asyncio.create_task(retry_all_connections())
    
    return {
        "message": f"Retrying {len(connections_to_retry)} connections",
        "retried_count": len(connections_to_retry),
        "daily_connections_used": today_connections,
        "daily_connections_remaining": remaining_slots
    }


@router.get("", response_model=List[ConnectionResponse])
def get_connections(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of connections"""
    query = db.query(Connection).join(Profile)

    if status:
        try:
            status_enum = ConnectionStatus(status)
            query = query.filter(Connection.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    connections = query.all()

    result = []
    for conn in connections:
        # Get the initial connection message if it exists
        connection_message = None
        connection_message_sent_at = None
        if conn.connection_message_id:
            message = db.query(Message).filter(Message.id == conn.connection_message_id).first()
            if message:
                connection_message = message.content
                connection_message_sent_at = message.sent_at.isoformat() if message.sent_at else None
        
        result.append(ConnectionResponse(
            id=conn.id,
            profile_id=conn.profile_id,
            profile_name=conn.profile.name,
            profile_url=conn.profile.linkedin_url,
            status=conn.status.value,
            connected_at=conn.connected_at.isoformat() if conn.connected_at else None,
            created_at=conn.created_at.isoformat() if conn.created_at else None,
            connection_message=connection_message,
            connection_message_sent_at=connection_message_sent_at,
            failure_reason=conn.failure_reason
        ))

    return result


@router.get("/{connection_id}", response_model=ConnectionResponse)
def get_connection(connection_id: int, db: Session = Depends(get_db)):
    """Get a single connection by ID"""
    connection = db.query(Connection).filter(Connection.id == connection_id).first()
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    # Get the initial connection message if it exists
    connection_message = None
    connection_message_sent_at = None
    if connection.connection_message_id:
        message = db.query(Message).filter(Message.id == connection.connection_message_id).first()
        if message:
            connection_message = message.content
            connection_message_sent_at = message.sent_at.isoformat() if message.sent_at else None
    
    return ConnectionResponse(
        id=connection.id,
        profile_id=connection.profile_id,
        profile_name=connection.profile.name,
        profile_url=connection.profile.linkedin_url,
        status=connection.status.value,
        connected_at=connection.connected_at.isoformat() if connection.connected_at else None,
        created_at=connection.created_at.isoformat() if connection.created_at else None,
        connection_message=connection_message,
        connection_message_sent_at=connection_message_sent_at,
        failure_reason=connection.failure_reason
    )

