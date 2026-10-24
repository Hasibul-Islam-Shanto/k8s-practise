import math

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, get_current_user_optional
from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostCreate, PostPage, PostRead, PostUpdate
from app.services.post_service import (
    get_or_create_tags,
    get_owned_post,
    get_post_read,
    list_posts,
    unique_post_slug,
)

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=PostPage)
def get_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    search: str | None = Query(None, max_length=200),
    tag: str | None = Query(None, max_length=60),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
) -> PostPage:
    items, total = list_posts(
        db,
        page=page,
        limit=limit,
        search=search,
        tag=tag,
        current_user_id=current_user.id if current_user else None,
    )
    return PostPage(
        items=items,
        page=page,
        limit=limit,
        total=total,
        total_pages=math.ceil(total / limit) if total else 0,
    )


@router.get("/{post_id}", response_model=PostRead)
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
) -> PostRead:
    return get_post_read(db, post_id, current_user.id if current_user else None)


@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(
    payload: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PostRead:
    post = Post(
        author_id=current_user.id,
        title=payload.title,
        slug=unique_post_slug(db, payload.title),
        excerpt=payload.excerpt,
        content=payload.content,
        tags=get_or_create_tags(db, payload.tags),
    )
    db.add(post)
    db.commit()
    return get_post_read(db, post.id, current_user.id)


@router.put("/{post_id}", response_model=PostRead)
def update_post(
    post_id: int,
    payload: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PostRead:
    post = get_owned_post(db, post_id, current_user)
    if payload.title != post.title:
        post.slug = unique_post_slug(db, payload.title, exclude_post_id=post.id)
    post.title = payload.title
    post.excerpt = payload.excerpt
    post.content = payload.content
    post.tags = get_or_create_tags(db, payload.tags)
    db.commit()
    return get_post_read(db, post.id, current_user.id)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    post = get_owned_post(db, post_id, current_user)
    db.delete(post)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
