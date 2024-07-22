from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials
from typing import Annotated
import schemas
import crud
import auth_handler

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=schemas.Token)
def signup(user: schemas.UserCreate):
    user_db = crud.create_user(user=user)
    if user_db:
        new_jwt_token = auth_handler.create_jwt_token({"email": user_db.email})
        return new_jwt_token


@router.post("/login", response_model=schemas.Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = schemas.UserLogin(email=form_data.username, password=form_data.password)
    user_db = crud.authenticate_user(user=user)
    if user_db:
        new_jwt_token = auth_handler.create_jwt_token({"email": user_db.email})
        return new_jwt_token


@router.get("/details")
def get_details(email: str = Depends(auth_handler.JWTBearer())):
    return {"email": email}

