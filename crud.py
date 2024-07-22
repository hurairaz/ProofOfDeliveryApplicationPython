from fastapi import HTTPException
from passlib.context import CryptContext
from contextlib import contextmanager
from database import SessionLocal
from models import User
import schemas

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
        return db.query(User).filter(User.email == email).first()


def get_user_by_username(username: str):
    """Get a user by username."""
    with session_scope() as db:
        return db.query(User).filter(User.username == username).first()


def authenticate_user(user: schemas.UserLogin):
    """Authenticate a user by email and password."""
    db_user = get_user_by_email(user.email)
    if not db_user or not verify_hash_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return db_user


def create_user(user: schemas.UserCreate):
    """Create a new user."""
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
