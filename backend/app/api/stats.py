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
    try:
        total_profiles = db.query(Profile).count() or 0
        
        total_connections = db.query(Connection).count() or 0
        
        connections_pending = db.query(Connection).filter(
            Connection.status == ConnectionStatus.PENDING
        ).count() or 0
        
        connections_connected = db.query(Connection).filter(
            Connection.status == ConnectionStatus.CONNECTED
        ).count() or 0
        
        connections_failed = db.query(Connection).filter(
            Connection.status == ConnectionStatus.FAILED
        ).count() or 0
        
        total_messages = db.query(Message).count() or 0
        
        initial_messages = db.query(Message).filter(
            Message.message_type == MessageType.INITIAL
        ).count() or 0
        
        followup_messages = db.query(Message).filter(
            Message.message_type == MessageType.FOLLOWUP
        ).count() or 0
        
        # Calculate response rate (connections that received follow-ups / total connected)
        # This is a simple metric - you might want to enhance it
        response_rate = 0.0
        try:
            if connections_connected > 0:
                connections_with_followups = db.query(Connection).join(Message).filter(
                    Connection.status == ConnectionStatus.CONNECTED,
                    Message.message_type == MessageType.FOLLOWUP
                ).distinct().count() or 0
                response_rate = float(connections_with_followups) / float(connections_connected) * 100.0
        except Exception as e:
            print(f"Error calculating response rate: {e}")
            response_rate = 0.0

        return StatsResponse(
            total_profiles=int(total_profiles),
            total_connections=int(total_connections),
            connections_pending=int(connections_pending),
            connections_connected=int(connections_connected),
            connections_failed=int(connections_failed),
            total_messages=int(total_messages),
            initial_messages=int(initial_messages),
            followup_messages=int(followup_messages),
            response_rate=float(round(response_rate, 2))
        )
    except Exception as e:
        print(f"Error in get_stats: {e}")
        import traceback
        traceback.print_exc()
        # Return default values on error
        return StatsResponse(
            total_profiles=0,
            total_connections=0,
            connections_pending=0,
            connections_connected=0,
            connections_failed=0,
            total_messages=0,
            initial_messages=0,
            followup_messages=0,
            response_rate=0.0
        )




