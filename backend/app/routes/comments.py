import math

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, literal, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.core.security import get_current_user, get_current_user_optional
from app.models.comment import Comment, CommentLike
from app.models.post import Post
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentPage, CommentRead, CommentUpdate
from app.schemas.post import LikeResponse

router = APIRouter(prefix="/posts", tags=["comments"])


def _require_post(db: Session, post_id: int) -> Post:
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


def _comment_on_post(db: Session, post_id: int, comment_id: int) -> Comment:
    _require_post(db, post_id)
    comment = db.get(Comment, comment_id)
    if comment is None or comment.post_id != post_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment


def _require_author(comment: Comment, user: User) -> None:
    if comment.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own comments",
        )


def _like_count(db: Session, comment_id: int) -> int:
    return (
        db.scalar(select(func.count(CommentLike.id)).where(CommentLike.comment_id == comment_id))
        or 0
    )


def _liked_by(db: Session, comment_id: int, user_id: int | None) -> bool:
    if user_id is None:
        return False
    count = db.scalar(
        select(func.count(CommentLike.id)).where(
            CommentLike.comment_id == comment_id,
            CommentLike.user_id == user_id,
        )
    )
    return bool(count)


def _to_read(db: Session, comment: Comment, current_user_id: int | None) -> CommentRead:
    return CommentRead(
        id=comment.id,
        post_id=comment.post_id,
        body=comment.body,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        author=comment.author,
        like_count=_like_count(db, comment.id),
        liked_by_current_user=_liked_by(db, comment.id, current_user_id),
    )


@router.get("/{post_id}/comments", response_model=CommentPage)
def list_comments(
    post_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
) -> CommentPage:
    _require_post(db, post_id)
    current_user_id = current_user.id if current_user else None
    like_count = (
        select(func.count(CommentLike.id))
        .where(CommentLike.comment_id == Comment.id)
        .correlate(Comment)
        .scalar_subquery()
    )
    if current_user_id is None:
        liked_expr = literal(0)
    else:
        liked_expr = (
            select(func.count(CommentLike.id))
            .where(CommentLike.comment_id == Comment.id, CommentLike.user_id == current_user_id)
            .correlate(Comment)
            .scalar_subquery()
        )
    total = db.scalar(select(func.count(Comment.id)).where(Comment.post_id == post_id)) or 0
    rows = db.execute(
        select(Comment, like_count.label("like_count"), liked_expr.label("liked"))
        .options(selectinload(Comment.author))
        .where(Comment.post_id == post_id)
        .order_by(Comment.created_at.asc(), Comment.id.asc())
        .offset((page - 1) * limit)
        .limit(limit)
    ).all()
    items = [
        CommentRead(
            id=comment.id,
            post_id=comment.post_id,
            body=comment.body,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            author=comment.author,
            like_count=count,
            liked_by_current_user=bool(liked),
        )
        for comment, count, liked in rows
    ]
    return CommentPage(
        items=items,
        page=page,
        limit=limit,
        total=total,
        total_pages=math.ceil(total / limit) if total else 0,
    )


@router.post("/{post_id}/comments", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
def create_comment(
    post_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommentRead:
    _require_post(db, post_id)
    comment = Comment(post_id=post_id, author_id=current_user.id, body=payload.body)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return _to_read(db, comment, current_user.id)


@router.put("/{post_id}/comments/{comment_id}", response_model=CommentRead)
def update_comment(
    post_id: int,
    comment_id: int,
    payload: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommentRead:
    comment = _comment_on_post(db, post_id, comment_id)
    _require_author(comment, current_user)
    comment.body = payload.body
    db.commit()
    db.refresh(comment)
    return _to_read(db, comment, current_user.id)


@router.delete("/{post_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    post_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    comment = _comment_on_post(db, post_id, comment_id)
    _require_author(comment, current_user)
    db.delete(comment)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{post_id}/comments/{comment_id}/like", response_model=LikeResponse)
def like_comment(
    post_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LikeResponse:
    comment = _comment_on_post(db, post_id, comment_id)
    db.add(CommentLike(user_id=current_user.id, comment_id=comment.id))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already liked this comment",
        ) from None
    return LikeResponse(liked=True, like_count=_like_count(db, comment.id))


@router.delete("/{post_id}/comments/{comment_id}/like", response_model=LikeResponse)
def unlike_comment(
    post_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LikeResponse:
    comment = _comment_on_post(db, post_id, comment_id)
    like = db.scalar(
        select(CommentLike).where(
            CommentLike.comment_id == comment.id,
            CommentLike.user_id == current_user.id,
        )
    )
    if like is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You have not liked this comment",
        )
    db.delete(like)
    db.commit()
    return LikeResponse(liked=False, like_count=_like_count(db, comment.id))
