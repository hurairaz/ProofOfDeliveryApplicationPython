from sqlalchemy import String, Integer, Boolean, Column, Enum, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import enum


class DispatchStatus(enum.Enum):
    pending = "pending"
    accepted = "accepted"
    started = "started"
    completed = "completed"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    dispatches = relationship("Dispatch", back_populates="delivery_person")


class Dispatch(Base):
    __tablename__ = "dispatches"

    id = Column(Integer, primary_key=True, index=True)
    area = Column(String, index=True)
    notes = Column(String, nullable=True)
    status = Column(Enum(DispatchStatus), default=DispatchStatus.pending)
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    start_time = Column(DateTime(timezone=True), nullable=True)
    complete_time = Column(DateTime(timezone=True), nullable=True)
    pod_image = Column(String, nullable=True)

    recipient_name = Column(String, nullable=True)
    delivery_person_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    delivery_person = relationship("User", back_populates="dispatches")

