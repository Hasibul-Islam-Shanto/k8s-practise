from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.user import UserAuthor

__all__ = ["CommentCreate", "CommentPage", "CommentRead", "CommentUpdate"]


class CommentBody(BaseModel):
    body: str = Field(min_length=1, max_length=2000)

    @field_validator("body")
    @classmethod
    def strip_body(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Comment cannot be empty")
        if len(stripped) > 2000:
            raise ValueError("Comment must be 2000 characters or fewer")
        return stripped


class CommentCreate(CommentBody):
    pass


class CommentUpdate(CommentBody):
    pass


class CommentRead(BaseModel):
    id: int
    post_id: int
    body: str
    created_at: datetime
    updated_at: datetime
    author: UserAuthor
    like_count: int
    liked_by_current_user: bool


class CommentPage(BaseModel):
    items: list[CommentRead]
    page: int
    limit: int
    total: int
    total_pages: int
