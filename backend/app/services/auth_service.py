from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.auth import RegisterRequest


def register_user(db: Session, payload: RegisterRequest) -> User:
    email = payload.email.lower()
    existing = db.scalar(
        select(User).where(or_(User.email == email, User.username == payload.username))
    )
    if existing is not None:
        field = "Email" if existing.email == email else "Username"
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{field} is already taken",
        )

    user = User(
        full_name=payload.full_name.strip(),
        username=payload.username,
        email=email,
        password_hash=hash_password(payload.password),
        bio=payload.bio.strip() if payload.bio else None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, identifier: str, password: str) -> User:
    identifier = identifier.strip()
    user = db.scalar(
        select(User).where(
            or_(
                func.lower(User.email) == identifier.lower(),
                User.username == identifier.lower(),
            )
        )
    )
    # Same message either way so the response cannot be used to enumerate accounts.
    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
        )
    return user
