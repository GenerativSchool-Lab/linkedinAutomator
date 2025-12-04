from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class ConnectionStatus(str, enum.Enum):
    PENDING = "pending"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    FAILED = "failed"
    REJECTED = "rejected"


class Connection(Base):
    __tablename__ = "connections"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    status = Column(SQLEnum(ConnectionStatus), default=ConnectionStatus.PENDING, nullable=False)
    connected_at = Column(DateTime(timezone=True), nullable=True)
    connection_message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    failure_reason = Column(String, nullable=True)  # Detailed reason for failure
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    profile = relationship("Profile", back_populates="connections")
    connection_message = relationship("Message", foreign_keys=[connection_message_id])
    messages = relationship("Message", back_populates="connection", foreign_keys="Message.connection_id")




