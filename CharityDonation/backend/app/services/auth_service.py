from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User, VolunteerStatus
from app.schemas.auth import LoginResponse, SignupResponse, UserResponse


def signup(
    db: Session,
    email: str,
    password: str,
    full_name: str,
    phone: str | None,
) -> SignupResponse:
    existing = db.scalar(select(User).where(User.email == email))
    if existing:
        raise ConflictError("Email already registered", "email_exists")

    user = User(
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        phone=phone,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    return SignupResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        is_volunteer=user.is_volunteer,
        volunteer_status=user.volunteer_status,
        is_available=user.is_available,
        access_token=token,
    )


def login(db: Session, email: str, password: str) -> LoginResponse:
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not verify_password(password, user.password_hash):
        raise UnauthorizedError("Invalid email or password", "invalid_credentials")

    token = create_access_token(user.id)
    return LoginResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


def get_user_response(user: User) -> UserResponse:
    return UserResponse.model_validate(user)
