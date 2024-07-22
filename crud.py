from fastapi import HTTPException, status, Depends
from database import SessionLocal
from contextlib import contextmanager
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from passlib.context import CryptContext
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
import schemas
from models import *


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


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
    return pwd_context.hash(password)


def verify_hash_password(plain_password: str, hash_password: str):
    return pwd_context.verify(plain_password, hash_password)


def get_user_by_email(email: str):
    with session_scope() as db:
        return db.query(User).filter(User.email == email).first()


def get_user_by_username(username: str):
    with session_scope() as db:
        return db.query(User).filter(User.username == username).first()


def authenticate_user(username: str, password: str):
    db_user = get_user_by_username(username)
    if not db_user or not verify_hash_password(password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return db_user


def create_access_token(data: dict):
    to_encode = data.copy()
    access_token_expires = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": access_token_expires})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user_db = get_user_by_username(token_data.username)
    if user_db is None:
        raise credentials_exception
    return user_db


def user_signup(user: schemas.UserCreate):
    if get_user_by_email(email=user.email) or get_user_by_username(
        username=user.username
    ):
        raise HTTPException(
            status_code=400, detail="Email or username already registered"
        )
    hashed_password = get_hash_password(password=user.password)
    new_user = User(
        username=user.username, email=user.email, hashed_password=hashed_password
    )
    with session_scope() as db:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user


def user_login(user: schemas.UserLogin):
    login_user = authenticate_user(username=user.username, password=user.password)
    if login_user:
        new_access_token = create_access_token(
            data={
                "sub": login_user.username,
            }
        )
        return {"access_token": new_access_token, "token_type": "bearer"}
