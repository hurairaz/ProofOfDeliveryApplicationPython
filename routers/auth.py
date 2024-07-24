from fastapi import APIRouter, Depends, HTTPException
import schemas
import crud
import auth_handler

router = APIRouter(prefix="/auth", tags=["Authentication Endpoints"])


@router.post("/signup", response_model=schemas.Token)
def signup(user: schemas.UserCreate):
    user_db = crud.create_user(user=user)
    if user_db:
        new_jwt_token = auth_handler.create_jwt_token({"email": user_db.email})
        return new_jwt_token


@router.post("/login", response_model=schemas.Token)
def login(user: schemas.UserLogin):
    user_db = crud.authenticate_user(user=user)
    if user_db:
        new_jwt_token = auth_handler.create_jwt_token({"email": user_db.email})
        return new_jwt_token
