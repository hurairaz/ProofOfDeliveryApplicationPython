from pydantic import BaseModel
from datetime import datetime
import enum
from typing import Optional


class DispatchStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    started = "started"
    completed = "completed"


class DispatchBase(BaseModel):
    area: str


class DispatchCreate(DispatchBase):
    pass


class Dispatch(DispatchBase):
    id: int
    notes: Optional[str] = None
    status: DispatchStatus
    create_time: datetime
    start_time: Optional[datetime] = None
    complete_time: Optional[datetime] = None
    pod_image: Optional[str] = None
    recipient_name: Optional[str] = None
    delivery_person_id: Optional[int] = None

    class Config:
        orm_mode = True


class DispatchResponse(BaseModel):
    id: int
    area: str
    status: DispatchStatus
    create_time: datetime


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    dispatches: list[Dispatch] = []

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    jwt_token: str
