from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.database import get_db
from app.models.profile import Profile
from app.models.connection import Connection, ConnectionStatus
from app.models.message import Message, MessageType
from pydantic import BaseModel

router = APIRouter()


class StatsResponse(BaseModel):
    total_profiles: int
    total_connections: int
    connections_pending: int
    connections_connected: int
    connections_failed: int
    total_messages: int
    initial_messages: int
    followup_messages: int
    response_rate: float


@router.get("", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    total_profiles = db.query(Profile).count()
    
    total_connections = db.query(Connection).count()
    
    connections_pending = db.query(Connection).filter(
        Connection.status == ConnectionStatus.PENDING
    ).count()
    
    connections_connected = db.query(Connection).filter(
        Connection.status == ConnectionStatus.CONNECTED
    ).count()
    
    connections_failed = db.query(Connection).filter(
        Connection.status == ConnectionStatus.FAILED
    ).count()
    
    total_messages = db.query(Message).count()
    
    initial_messages = db.query(Message).filter(
        Message.message_type == MessageType.INITIAL
    ).count()
    
    followup_messages = db.query(Message).filter(
        Message.message_type == MessageType.FOLLOWUP
    ).count()
    
    # Calculate response rate (connections that received follow-ups / total connected)
    # This is a simple metric - you might want to enhance it
    response_rate = 0.0
    if connections_connected > 0:
        connections_with_followups = db.query(Connection).join(Message).filter(
            Connection.status == ConnectionStatus.CONNECTED,
            Message.message_type == MessageType.FOLLOWUP
        ).distinct().count()
        response_rate = (connections_with_followups / connections_connected) * 100

    return StatsResponse(
        total_profiles=total_profiles,
        total_connections=total_connections,
        connections_pending=connections_pending,
        connections_connected=connections_connected,
        connections_failed=connections_failed,
        total_messages=total_messages,
        initial_messages=initial_messages,
        followup_messages=followup_messages,
        response_rate=round(response_rate, 2)
    )




