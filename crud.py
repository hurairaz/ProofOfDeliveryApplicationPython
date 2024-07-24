from fastapi import HTTPException
from passlib.context import CryptContext
from contextlib import contextmanager
from database import SessionLocal
from models import *
import schemas
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import func

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
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_hash_password(plain_password: str, hashed_password: str):
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_user_by_email(email: str):
    """Retrieve a user from the database by their email address."""
    with session_scope() as db:
        user = db.query(User).filter(User.email == email).first()
        return user


def get_user_by_username(username: str):
    """Retrieve a user from the database by their username."""
    with session_scope() as db:
        user = db.query(User).filter(User.username == username).first()
        return user


def authenticate_user(user: schemas.UserLogin):
    """Authenticate a user by email and password.

    Raises:
        HTTPException: 404 if the user is not found or password is incorrect.
    """
    db_user = get_user_by_email(user.email)
    if db_user:
        if not verify_hash_password(user.password, db_user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid password")
        return db_user
    else:
        raise HTTPException(status_code=404, detail="User not found")


def create_user(user: schemas.UserCreate):
    """Create a new user in the database.

    Raises:
        HTTPException: 400 if the email is already registered.
    """
    if get_user_by_email(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_hash_password(user.password)
    new_user = User(
        username=user.username, email=user.email, hashed_password=hashed_password
    )
    with session_scope() as db:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user


def create_dispatch(dispatch: schemas.DispatchCreate):
    """Create a new dispatch record in the database."""
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
    date: Optional[str] = None,
):
    """Filter dispatches based on various parameters.

    Args:
        skip: Number of records to skip.
        limit: Number of records to return.
        dispatch_id: Filter by dispatch ID.
        area: Filter by dispatch area.
        status: Filter by dispatch status.
        delivery_person_id: Filter by delivery person ID.
        date: Filter by dispatch creation date (Y-m-d).
    """
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
            try:
                actual_date = datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Error parsing date: {e}")
            query = query.filter(func.date(Dispatch.create_time) == actual_date)

        if skip is not None:
            query = query.offset(skip)

        if limit is not None:
            query = query.limit(limit)

        return query.all()


def accept_dispatch(dispatch_id: int, user_email: str):
    """Accept a dispatch and assign it to a user.

    Args:
        dispatch_id: ID of the dispatch to be accepted.
        user_email: Email of the user accepting the dispatch.

    Raises:
        HTTPException: 404 if dispatch or user is not found, or if dispatch is not in a pending state.
    """
    with session_scope() as db:
        dispatch_db = db.query(Dispatch).filter(Dispatch.id == dispatch_id).first()
        if not dispatch_db:
            raise HTTPException(status_code=404, detail="Dispatch not found")

        user_db = db.query(User).filter(User.email == user_email).first()
        if not user_db:
            raise HTTPException(status_code=404, detail="User not found")

        if dispatch_db.status != DispatchStatus.pending:
            raise HTTPException(
                status_code=404, detail="Dispatch not available for acceptance"
            )

        dispatch_db.status = DispatchStatus.accepted
        dispatch_db.delivery_person_id = user_db.id

        db.commit()
        db.refresh(dispatch_db)
        db.refresh(user_db)

        return dispatch_db


def start_dispatch(dispatch_id: int, user_email: str):
    """Start a dispatch if it is assigned to the user.

    Args:
        dispatch_id: ID of the dispatch to start.
        user_email: Email of the user starting the dispatch.

    Raises:
        HTTPException: 404 if dispatch or user is not found, or if dispatch is not assigned to the user.
    """
    with session_scope() as db:
        dispatch_db = db.query(Dispatch).filter(Dispatch.id == dispatch_id).first()
        if not dispatch_db:
            raise HTTPException(status_code=404, detail="Dispatch not found")

        user_db = db.query(User).filter(User.email == user_email).first()
        if not user_db:
            raise HTTPException(status_code=404, detail="User not found")

        if dispatch_db.delivery_person_id != user_db.id:
            raise HTTPException(
                status_code=404, detail="Dispatch not assigned to this user"
            )

        dispatch_db.status = DispatchStatus.started
        dispatch_db.start_time = datetime.now(timezone.utc)

        db.commit()
        db.refresh(dispatch_db)
        return dispatch_db


def get_user_dispatches(user_email: str):
    """Retrieve all dispatches assigned to a user.

    Args:
        user_email: Email of the user whose dispatches are to be retrieved.

    Raises:
        HTTPException: 404 if user is not found.
    """
    with session_scope() as db:
        user_db = db.query(User).filter(User.email == user_email).first()

        if not user_db:
            raise HTTPException(status_code=404, detail="User not found")

        return user_db.dispatches


def get_delivery_person(dispatch_id: int):
    """Retrieve the delivery person assigned to a dispatch.

    Args:
        dispatch_id: ID of the dispatch.

    Raises:
        HTTPException: 404 if dispatch is not found.
    """
    with session_scope() as db:
        dispatch_db = db.query(Dispatch).filter(Dispatch.id == dispatch_id).first()
        if not dispatch_db:
            raise HTTPException(status_code=404, detail="Dispatch not found")

        return dispatch_db.delivery_person


def complete_dispatch(
    user_email: str,
    dispatch_id: int,
    recipient_name: str,
    pod_image: Optional[str] = None,
    notes: Optional[str] = None,
):
    """Complete a dispatch and update its details.

    Args:
        user_email: Email of the user completing the dispatch.
        dispatch_id: ID of the dispatch to be completed.
        recipient_name: Name of the recipient.
        pod_image: Optional image of the POD (proof of delivery).
        notes: Optional notes for the dispatch.

    Raises:
        HTTPException: 404 if dispatch or user is not found, or if dispatch is not assigned to the user or already completed.
    """
    with session_scope() as db:
        dispatch_db = db.query(Dispatch).filter(Dispatch.id == dispatch_id).first()
        if not dispatch_db:
            raise HTTPException(status_code=404, detail="Dispatch not found")

        user_db = db.query(User).filter(User.email == user_email).first()
        if not user_db:
            raise HTTPException(status_code=404, detail="User not found")

        if dispatch_db.delivery_person_id != user_db.id:
            raise HTTPException(
                status_code=404, detail="Dispatch not assigned to this user"
            )

        if dispatch_db.status != DispatchStatus.started:
            raise HTTPException(status_code=404, detail="Dispatch has not yet started")

        if dispatch_db.status == DispatchStatus.completed:
            raise HTTPException(
                status_code=404, detail="Dispatch has already been completed"
            )

        dispatch_db.status = DispatchStatus.completed
        dispatch_db.recipient_name = recipient_name
        dispatch_db.complete_time = datetime.now(timezone.utc)
        if pod_image:
            dispatch_db.pod_image = pod_image
        if notes:
            dispatch_db.notes = notes

        db.commit()
        db.refresh(dispatch_db)
        return dispatch_db
