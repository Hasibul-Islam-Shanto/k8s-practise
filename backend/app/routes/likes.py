from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.like import Like
from app.models.post import Post
from app.models.user import User
from app.schemas.post import LikeResponse

router = APIRouter(prefix="/posts", tags=["likes"])


def _require_post(db: Session, post_id: int) -> Post:
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


def _like_count(db: Session, post_id: int) -> int:
    return db.scalar(select(func.count(Like.id)).where(Like.post_id == post_id)) or 0


@router.post("/{post_id}/like", response_model=LikeResponse)
def like_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LikeResponse:
    _require_post(db, post_id)
    db.add(Like(user_id=current_user.id, post_id=post_id))
    try:
        db.commit()
    except IntegrityError:
        # The unique constraint on (user_id, post_id) is the real guard here.
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already liked this post",
        ) from None
    return LikeResponse(liked=True, like_count=_like_count(db, post_id))


@router.delete("/{post_id}/like", response_model=LikeResponse)
def unlike_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LikeResponse:
    _require_post(db, post_id)
    like = db.scalar(
        select(Like).where(Like.post_id == post_id, Like.user_id == current_user.id)
    )
    if like is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You have not liked this post",
        )
    db.delete(like)
    db.commit()
    return LikeResponse(liked=False, like_count=_like_count(db, post_id))
