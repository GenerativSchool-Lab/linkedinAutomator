from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
import asyncio
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db, SessionLocal
from app.models.connection import Connection, ConnectionStatus
from app.models.message import Message, MessageType
from app.models.followup import FollowUp, FollowUpStatus
from app.services.linkedin import linkedin_service
from app.services.message_generator import message_generator
from app.config import settings
from pydantic import BaseModel

router = APIRouter()


class MessageResponse(BaseModel):
    id: int
    connection_id: int
    profile_name: str
    profile_url: str
    content: str
    message_type: str
    sent_at: str
    created_at: str

    class Config:
        from_attributes = True


class SendFollowUpRequest(BaseModel):
    connection_id: int


async def send_followup_message(connection_id: int):
    """Background task to send a follow-up message"""
    db = SessionLocal()
    try:
        connection = db.query(Connection).filter(Connection.id == connection_id).first()
        if not connection:
            return

        if connection.status != ConnectionStatus.CONNECTED:
            return

        # Get previous messages
        previous_messages = db.query(Message).filter(
            Message.connection_id == connection_id
        ).order_by(Message.sent_at).all()

        # Generate follow-up message
        message_content = message_generator.generate_followup_message(
            connection.profile,
            previous_messages
        )

        # Send message
        import asyncio
        await asyncio.sleep(settings.rate_limit_delay)
        success = await linkedin_service.send_message(
            connection.profile.linkedin_url,
            message_content
        )

        if success:
            # Create message record
            message = Message(
                connection_id=connection_id,
                content=message_content,
                message_type=MessageType.FOLLOWUP
            )
            db.add(message)
            db.commit()

            # Update follow-up status if exists
            followup = db.query(FollowUp).filter(
                FollowUp.message_id == connection.connection_message_id
            ).filter(FollowUp.status == FollowUpStatus.PENDING).first()
            
            if followup:
                followup.status = FollowUpStatus.SENT
                followup.sent_at = datetime.utcnow()
                db.commit()
        else:
            # Mark follow-up as failed
            followup = db.query(FollowUp).filter(
                FollowUp.message_id == connection.connection_message_id
            ).filter(FollowUp.status == FollowUpStatus.PENDING).first()
            
            if followup:
                followup.status = FollowUpStatus.FAILED
                db.commit()

    except Exception as e:
        print(f"Error sending follow-up for connection {connection_id}: {e}")
    finally:
        db.close()


@router.get("", response_model=List[MessageResponse])
def get_messages(
    connection_id: Optional[int] = None,
    message_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get message history"""
    query = db.query(Message).join(Connection, Message.connection_id == Connection.id).join(Connection.profile)

    if connection_id:
        query = query.filter(Message.connection_id == connection_id)

    if message_type:
        try:
            msg_type_enum = MessageType(message_type)
            query = query.filter(Message.message_type == msg_type_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid message type: {message_type}")

    messages = query.order_by(Message.sent_at.desc()).all()

    result = []
    for msg in messages:
        result.append(MessageResponse(
            id=msg.id,
            connection_id=msg.connection_id,
            profile_name=msg.connection.profile.name,
            profile_url=msg.connection.profile.linkedin_url,
            content=msg.content,
            message_type=msg.message_type.value,
            sent_at=msg.sent_at.isoformat() if msg.sent_at else None,
            created_at=msg.created_at.isoformat() if msg.created_at else None
        ))

    return result


@router.post("/send-followup")
async def send_followup(
    request: SendFollowUpRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Manually trigger a follow-up message"""
    connection = db.query(Connection).filter(Connection.id == request.connection_id).first()
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    if connection.status != ConnectionStatus.CONNECTED:
        raise HTTPException(status_code=400, detail="Connection must be connected to send follow-up")

    asyncio.create_task(send_followup_message(request.connection_id))

    return {"message": "Follow-up message queued"}


@router.get("/{message_id}", response_model=MessageResponse)
def get_message(message_id: int, db: Session = Depends(get_db)):
    """Get a single message by ID"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    return MessageResponse(
        id=message.id,
        connection_id=message.connection_id,
        profile_name=message.connection.profile.name,
        profile_url=message.connection.profile.linkedin_url,
        content=message.content,
        message_type=message.message_type.value,
        sent_at=message.sent_at.isoformat() if message.sent_at else None,
        created_at=message.created_at.isoformat() if message.created_at else None
    )

