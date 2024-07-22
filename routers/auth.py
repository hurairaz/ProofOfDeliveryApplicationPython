from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
import schemas
import crud

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=schemas.User)
def signup(user: schemas.UserCreate):
    return crud.user_signup(user)


@router.post("/login", response_model=schemas.Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = schemas.UserLogin(username=form_data.username, password=form_data.password)
    return crud.user_login(user)


@router.post("/refresh", response_model=schemas.Token)
def refresh(user: Annotated[schemas.User, Depends(crud.get_current_user)]):
    if user:
        new_access_token = crud.create_access_token(
            data={
                "sub": user.username,
            }
        )
        return {"access_token": new_access_token, "token_type": "bearer"}
