from fastapi import HTTPException
from passlib.context import CryptContext
from contextlib import contextmanager
from database import SessionLocal
from models import *
import schemas
from typing import Optional
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@contextmanager
def session_scope():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def get_hash_password(password: str):
    """Hash a password."""
    return pwd_context.hash(password)

def verify_hash_password(plain_password: str, hashed_password: str):
    """Verify a password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_email(email: str):
    """Get a user by email."""
    with session_scope() as db:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

def get_user_by_username(username: str):
    """Get a user by username."""
    with session_scope() as db:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

def authenticate_user(user: schemas.UserLogin):
    """Authenticate a user by email and password."""
    db_user = get_user_by_email(user.email)
    if not verify_hash_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid password")
    return db_user

def create_user(user: schemas.UserCreate):
    """Create a new user."""
    if get_user_by_email(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_hash_password(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    with session_scope() as db:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

def create_dispatch(dispatch: schemas.DispatchCreate):
    """Create a new dispatch."""
    new_dispatch = Dispatch(area=dispatch.area)
    with session_scope() as db:
        db.add(new_dispatch)
        db.commit()
        db.refresh(new_dispatch)
        return new_dispatch

def filter_dispatches(
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        dispatch_id: Optional[int] = None,
        area: Optional[str] = None,
        status: Optional[schemas.DispatchStatus] = None,
        delivery_person_id: Optional[int] = None,
        date: Optional[datetime] = None
):
    """Filter dispatches based on various params."""
    with session_scope() as db:
        query = db.query(Dispatch)

        if dispatch_id is not None:
            query = query.filter(Dispatch.id == dispatch_id)

        if area is not None:
            query = query.filter(Dispatch.area == area)

        if status is not None:
            query = query.filter(Dispatch.status == status)

        if delivery_person_id is not None:
            query = query.filter(Dispatch.delivery_person_id == delivery_person_id)

        if date is not None:
            query = query.filter(Dispatch.create_time == date)

        if skip is not None:
            query = query.offset(skip)

        if limit is not None:
            query = query.limit(limit)

        return query.all()

def accept_dispatch(dispatch_id: int, user_email: str):
    """Accept a dispatch and assign it to a user."""
    with session_scope() as db:
        # Fetch the dispatch by ID
        dispatch_db = db.query(Dispatch).filter(Dispatch.id == dispatch_id).first()
        if not dispatch_db:
            raise HTTPException(status_code=404, detail="Dispatch not found")

        # Ensure the dispatch status is of the correct enum type
        if not isinstance(dispatch_db.status, DispatchStatus):
            raise HTTPException(status_code=500, detail="Dispatch status type mismatch")

        # Fetch the user by email
        user_db = db.query(User).filter(User.email == user_email).first()
        if not user_db:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if the dispatch status is 'pending'
        if dispatch_db.status != DispatchStatus.pending:
            raise HTTPException(status_code=400, detail="Dispatch not available for acceptance")

        # Update the dispatch status and assign it to the user
        dispatch_db.status = DispatchStatus.accepted
        dispatch_db.delivery_person_id = user_db.id

        # Commit the changes to the database
        db.commit()
        db.refresh(dispatch_db)
        db.refresh(user_db)

        return dispatch_db

def start_dispatch(dispatch_id: int, user_email: str):
    """Start a dispatch if it is assigned to the user."""
    with session_scope() as db:
        dispatch_db = db.query(Dispatch).filter(Dispatch.id == dispatch_id).first()
        if not dispatch_db:
            raise HTTPException(status_code=404, detail="Dispatch not found")

        user_db = db.query(User).filter(User.email == user_email).first()
        if not user_db:
            raise HTTPException(status_code=404, detail="User not found")

        if dispatch_db.delivery_person_id != user_db.id:
            raise HTTPException(status_code=403, detail="Dispatch not assigned to this user")

        dispatch_db.status = schemas.DispatchStatus.started
        dispatch_db.start_time = datetime.now()

        db.commit()
        db.refresh(dispatch_db)
        return dispatch_db

def get_user_dispatches(user_email: str):
    """Get all dispatches assigned to a user."""
    user_db = get_user_by_email(email=user_email)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    return user_db.dispatches
