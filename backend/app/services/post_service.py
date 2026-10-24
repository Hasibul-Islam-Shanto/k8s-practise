import re

from fastapi import HTTPException, status
from sqlalchemy import Select, func, literal, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.like import Like
from app.models.post import Post, post_tags
from app.models.tag import Tag
from app.models.user import User
from app.schemas.post import PostRead

SLUG_STRIP = re.compile(r"[^a-z0-9]+")


def slugify(value: str) -> str:
    slug = SLUG_STRIP.sub("-", value.casefold()).strip("-")
    return slug or "post"


def unique_post_slug(db: Session, title: str, exclude_post_id: int | None = None) -> str:
    base = slugify(title)[:200]
    candidate = base
    suffix = 2
    while True:
        query = select(Post.id).where(Post.slug == candidate)
        if exclude_post_id is not None:
            query = query.where(Post.id != exclude_post_id)
        if db.scalar(query) is None:
            return candidate
        candidate = f"{base}-{suffix}"
        suffix += 1


def get_or_create_tags(db: Session, names: list[str]) -> list[Tag]:
    """Reuse existing tags case-insensitively so 'Vue' and 'vue' don't diverge."""
    tags: list[Tag] = []
    for name in names:
        slug = slugify(name)
        tag = db.scalar(select(Tag).where(Tag.slug == slug))
        if tag is None:
            tag = Tag(name=name, slug=slug)
            db.add(tag)
            db.flush()
        tags.append(tag)
    return tags


def _post_select(current_user_id: int | None) -> Select:
    """Select posts alongside their like count and the viewer's like state.

    Correlated subqueries keep this to one query regardless of page size, and
    avoid the GROUP BY that a join against `likes` would require.
    """
    like_count = (
        select(func.count(Like.id))
        .where(Like.post_id == Post.id)
        .correlate(Post)
        .scalar_subquery()
    )
    if current_user_id is None:
        liked_expr = literal(0)
    else:
        liked_expr = (
            select(func.count(Like.id))
            .where(Like.post_id == Post.id, Like.user_id == current_user_id)
            .correlate(Post)
            .scalar_subquery()
        )
    return (
        select(Post, like_count.label("like_count"), liked_expr.label("liked"))
        .options(selectinload(Post.author), selectinload(Post.tags))
    )


def serialize_post(post: Post, like_count: int, liked: bool) -> PostRead:
    return PostRead.model_validate(
        {
            "id": post.id,
            "title": post.title,
            "slug": post.slug,
            "excerpt": post.excerpt,
            "content": post.content,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
            "author": post.author,
            "tags": sorted(post.tags, key=lambda t: t.name.casefold()),
            "like_count": like_count,
            "liked_by_current_user": liked,
        },
        from_attributes=True,
    )


def list_posts(
    db: Session,
    *,
    page: int,
    limit: int,
    search: str | None = None,
    tag: str | None = None,
    author_username: str | None = None,
    current_user_id: int | None = None,
) -> tuple[list[PostRead], int]:
    filters = []
    if search:
        pattern = f"%{search.strip()}%"
        # Match the post title, the author's name/username, or a tag name.
        tag_match = (
            select(post_tags.c.post_id)
            .join(Tag, Tag.id == post_tags.c.tag_id)
            .where(Tag.name.ilike(pattern))
        )
        filters.append(
            or_(
                Post.title.ilike(pattern),
                Post.excerpt.ilike(pattern),
                Post.author.has(or_(User.full_name.ilike(pattern), User.username.ilike(pattern))),
                Post.id.in_(tag_match),
            )
        )
    if tag:
        tag_slug = slugify(tag)
        filters.append(
            Post.id.in_(
                select(post_tags.c.post_id)
                .join(Tag, Tag.id == post_tags.c.tag_id)
                .where(Tag.slug == tag_slug)
            )
        )
    if author_username:
        filters.append(Post.author.has(User.username == author_username.lower()))

    total = db.scalar(select(func.count(Post.id)).where(*filters)) or 0

    rows = db.execute(
        _post_select(current_user_id)
        .where(*filters)
        .order_by(Post.created_at.desc(), Post.id.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    ).all()

    items = [serialize_post(post, count, bool(liked)) for post, count, liked in rows]
    return items, total


def get_post_read(db: Session, post_id: int, current_user_id: int | None) -> PostRead:
    row = db.execute(_post_select(current_user_id).where(Post.id == post_id)).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    post, count, liked = row
    return serialize_post(post, count, bool(liked))


def get_owned_post(db: Session, post_id: int, user: User) -> Post:
    """Fetch a post and confirm the caller owns it. Authorization lives here so
    every write path goes through the same check."""
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own posts",
        )
    return post
