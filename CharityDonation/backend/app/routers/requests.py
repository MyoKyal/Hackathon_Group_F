from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.request import RequestCreate, RequestResponse, RequestUpdate
from app.services import request_service

router = APIRouter(prefix="/requests", tags=["requests"])


@router.post("", response_model=RequestResponse, status_code=201)
def create_request(
    payload: RequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return request_service.create_request(db, current_user, payload)


@router.get("", response_model=list[RequestResponse])
def list_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return request_service.list_requests(db, current_user)


@router.get("/{request_id}", response_model=RequestResponse)
def get_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return request_service.get_request(db, current_user, request_id)


@router.patch("/{request_id}", response_model=RequestResponse)
def update_request(
    request_id: UUID,
    payload: RequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return request_service.update_request(db, current_user, request_id, payload)
