from sqlalchemy import (
    String,
    Integer,
    Boolean,
    Column,
    Enum,
    DateTime,
    func,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from database import Base
import enum


class DispatchStatus(enum.Enum):
    """Enumeration of possible dispatch statuses."""

    pending = "pending"
    accepted = "accepted"
    started = "started"
    completed = "completed"


class User(Base):
    """Database model for users.

    Attributes:
        id (int): Unique identifier for the user.
        username (str): Username of the user.
        email (str): Email address of the user.
        hashed_password (str): Hashed password of the user.
        is_active (bool): Indicates if the user's account is active.
        dispatches (relationship): Relationship to the Dispatch model indicating dispatches assigned to the user.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    dispatches = relationship("Dispatch", back_populates="delivery_person")


class Dispatch(Base):
    """Database model for dispatches.

    Attributes:
        id (int): Unique identifier for the dispatch.
        area (str): Area where the dispatch is to be delivered.
        notes (str): Optional notes about the dispatch.
        status (DispatchStatus): Current status of the dispatch.
        create_time (datetime): Timestamp when the dispatch was created.
        start_time (datetime): Timestamp when the dispatch was started.
        complete_time (datetime): Timestamp when the dispatch was completed.
        pod_image (str): Optional image of the proof of delivery.
        recipient_name (str): Name of the recipient.
        delivery_person_id (int): Foreign key referencing the user assigned to the dispatch.
        delivery_person (relationship): Relationship to the User model indicating the delivery person assigned to the dispatch.
    """

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
