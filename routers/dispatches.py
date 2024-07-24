from fastapi import APIRouter, Depends
from typing import Optional
import schemas
import crud
import auth_handler

router = APIRouter(prefix="/dispatches", tags=["Dispatches Endpoints"])


@router.get("/", response_model=list[schemas.DispatchResponse])
def get_available_dispatches(dependency: str = Depends(auth_handler.JWTBearer())):
    return crud.filter_dispatches(status=schemas.DispatchStatus.pending)


@router.get("/filter", response_model=list[schemas.DispatchResponse])
def filter_dispatches(
    skip: Optional[int] = None,
    limit: Optional[int] = None,
    dispatch_id: Optional[int] = None,
    area: Optional[str] = None,
    status: Optional[schemas.DispatchStatus] = None,
    delivery_person_id: Optional[int] = None,
    date: Optional[str] = None,
    dependency: str = Depends(auth_handler.JWTBearer()),
):
    return crud.filter_dispatches(
        skip, limit, dispatch_id, area, status, delivery_person_id, date
    )


@router.get("/{dispatch_id}", response_model=list[schemas.DispatchResponse])
def get_dispatch(dispatch_id: int, dependency: str = Depends(auth_handler.JWTBearer())):
    return crud.filter_dispatches(dispatch_id=dispatch_id)


@router.post("/{dispatch_id}/start", response_model=schemas.Dispatch)
def start_dispatch(dispatch_id: int, email: str = Depends(auth_handler.JWTBearer())):
    return crud.start_dispatch(dispatch_id=dispatch_id, user_email=email)


@router.post("/{dispatch_id}/complete", response_model=schemas.Dispatch)
def complete_dispatch(
    dispatch_id: int,
    recipient_name: str,
    pod_image: Optional[str] = None,
    notes: Optional[str] = None,
    user_email: str = Depends(auth_handler.JWTBearer()),
):
    return crud.complete_dispatch(
        user_email, dispatch_id, recipient_name, pod_image, notes
    )


@router.post("/{dispatch_id}/accept", response_model=schemas.Dispatch)
def accept_dispatch(dispatch_id: int, email: str = Depends(auth_handler.JWTBearer())):
    return crud.accept_dispatch(dispatch_id=dispatch_id, user_email=email)


@router.post("/create", response_model=schemas.Dispatch)
def create_dispatch(
    dispatch: schemas.DispatchCreate,
    dependency: str = Depends(auth_handler.JWTBearer()),
):
    return crud.create_dispatch(dispatch=dispatch)


@router.get("/{dispatch_id}/delivery_person")
def get_delivery_person(dispatch_id: int):
    return crud.get_delivery_person(dispatch_id)
