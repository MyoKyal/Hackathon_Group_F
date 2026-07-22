from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, SignupRequest, SignupResponse, UserResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    return auth_service.signup(
        db, payload.email, payload.password, payload.full_name, payload.phone
    )


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.login(db, payload.email, payload.password)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout():
    # Client discards token; no server-side blocklist in scope.
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return auth_service.get_user_response(current_user)
