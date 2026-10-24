import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, get_current_user_optional
from app.models.like import Like
from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostPage
from app.schemas.user import UserProfile, UserRead, UserUpdate
from app.services.post_service import list_posts

router = APIRouter(prefix="/users", tags=["users"])


def _require_user(db: Session, username: str) -> User:
    user = db.scalar(select(User).where(User.username == username.lower()))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def _build_profile(db: Session, user: User) -> UserProfile:
    post_count = db.scalar(select(func.count(Post.id)).where(Post.author_id == user.id)) or 0
    total_likes = (
        db.scalar(
            select(func.count(Like.id))
            .join(Post, Post.id == Like.post_id)
            .where(Post.author_id == user.id)
        )
        or 0
    )
    return UserProfile.model_validate(
        {
            "id": user.id,
            "full_name": user.full_name,
            "username": user.username,
            "avatar_url": user.avatar_url,
            "bio": user.bio,
            "created_at": user.created_at,
            "post_count": post_count,
            "total_likes_received": total_likes,
        }
    )


@router.put("/me", response_model=UserRead)
def update_own_profile(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserRead:
    # Only ever writes to the authenticated user, so there is no way to target
    # somebody else's profile.
    fields = payload.model_dump(exclude_unset=True)
    if "full_name" in fields and fields["full_name"]:
        current_user.full_name = fields["full_name"].strip()
    if "bio" in fields:
        bio = fields["bio"]
        current_user.bio = bio.strip() if bio and bio.strip() else None
    if "avatar_url" in fields:
        current_user.avatar_url = fields["avatar_url"]
    db.commit()
    db.refresh(current_user)
    return UserRead.model_validate(current_user, from_attributes=True)


@router.get("/{username}", response_model=UserProfile)
def get_profile(username: str, db: Session = Depends(get_db)) -> UserProfile:
    return _build_profile(db, _require_user(db, username))


@router.get("/{username}/posts", response_model=PostPage)
def get_user_posts(
    username: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
) -> PostPage:
    user = _require_user(db, username)
    items, total = list_posts(
        db,
        page=page,
        limit=limit,
        author_username=user.username,
        current_user_id=current_user.id if current_user else None,
    )
    return PostPage(
        items=items,
        page=page,
        limit=limit,
        total=total,
        total_pages=math.ceil(total / limit) if total else 0,
    )
