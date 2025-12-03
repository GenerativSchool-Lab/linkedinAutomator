from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.connection import Connection, ConnectionStatus
from app.models.message import Message, MessageType
from app.models.followup import FollowUp, FollowUpStatus
from app.services.linkedin import linkedin_service
from app.services.message_generator import message_generator
from app.config import settings
import asyncio

scheduler = AsyncIOScheduler()


async def process_pending_followups():
    """Process all pending follow-ups that are due"""
    db: Session = SessionLocal()
    try:
        # Get all pending follow-ups that are due
        now = datetime.utcnow()
        pending_followups = db.query(FollowUp).filter(
            FollowUp.status == FollowUpStatus.PENDING,
            FollowUp.scheduled_at <= now
        ).all()

        for followup in pending_followups:
            try:
                message = followup.message
                connection = message.connection

                if connection.status != ConnectionStatus.CONNECTED:
                    followup.status = FollowUpStatus.CANCELLED
                    db.commit()
                    continue

                # Get previous messages for context
                previous_messages = db.query(Message).filter(
                    Message.connection_id == connection.id
                ).order_by(Message.sent_at).all()

                # Generate follow-up message
                followup_content = message_generator.generate_followup_message(
                    connection.profile,
                    previous_messages
                )

                # Send message
                await asyncio.sleep(settings.rate_limit_delay)
                success = await linkedin_service.send_message(
                    connection.profile.linkedin_url,
                    followup_content
                )

                if success:
                    # Create new message record
                    new_message = Message(
                        connection_id=connection.id,
                        content=followup_content,
                        message_type=MessageType.FOLLOWUP
                    )
                    db.add(new_message)
                    db.commit()
                    db.refresh(new_message)

                    # Update follow-up status
                    followup.status = FollowUpStatus.SENT
                    followup.sent_at = datetime.utcnow()
                    db.commit()
                else:
                    followup.status = FollowUpStatus.FAILED
                    db.commit()

            except Exception as e:
                print(f"Error processing follow-up {followup.id}: {e}")
                followup.status = FollowUpStatus.FAILED
                db.commit()

    finally:
        db.close()


async def schedule_followups_for_new_connections():
    """Schedule follow-ups for newly connected profiles"""
    db: Session = SessionLocal()
    try:
        # Find connections that have initial messages but no scheduled follow-up
        connections = db.query(Connection).join(Message).filter(
            Connection.status == ConnectionStatus.CONNECTED,
            Message.message_type == MessageType.INITIAL,
            Message.id == Connection.connection_message_id
        ).all()

        for connection in connections:
            # Check if follow-up already scheduled
            existing_followup = db.query(FollowUp).filter(
                FollowUp.message_id == connection.connection_message_id
            ).first()

            if not existing_followup:
                # Schedule follow-up
                followup_date = datetime.utcnow() + timedelta(days=settings.followup_days)
                followup = FollowUp(
                    message_id=connection.connection_message_id,
                    scheduled_at=followup_date,
                    status=FollowUpStatus.PENDING
                )
                db.add(followup)
                db.commit()

    finally:
        db.close()


def start_scheduler():
    """Start the background scheduler"""
    # Schedule follow-up processing every hour
    scheduler.add_job(
        process_pending_followups,
        trigger=IntervalTrigger(hours=1),
        id="process_followups",
        replace_existing=True
    )

    # Schedule follow-up creation check every 6 hours
    scheduler.add_job(
        schedule_followups_for_new_connections,
        trigger=IntervalTrigger(hours=6),
        id="schedule_followups",
        replace_existing=True
    )

    # Start scheduler
    scheduler.start()


def stop_scheduler():
    """Stop the scheduler"""
    scheduler.stop()

