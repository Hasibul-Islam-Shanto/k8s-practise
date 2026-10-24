from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.user import UserAuthor

MAX_TAGS_PER_POST = 5


class TagRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str


class PostBase(BaseModel):
    title: str = Field(min_length=5, max_length=200)
    excerpt: str = Field(min_length=10, max_length=500)
    content: str = Field(min_length=50, max_length=50_000)
    tags: list[str] = Field(min_length=1, max_length=MAX_TAGS_PER_POST)

    @field_validator("title", "excerpt", "content")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("tags")
    @classmethod
    def clean_tags(cls, values: list[str]) -> list[str]:
        cleaned: list[str] = []
        seen: set[str] = set()
        for raw in values:
            name = raw.strip()
            if not name:
                continue
            if len(name) > 60:
                raise ValueError("Tag names must be 60 characters or fewer")
            key = name.casefold()
            if key not in seen:
                seen.add(key)
                cleaned.append(name)
        if not cleaned:
            raise ValueError("At least one technology tag is required")
        return cleaned


class PostCreate(PostBase):
    pass


class PostUpdate(PostBase):
    pass


class PostRead(BaseModel):
    id: int
    title: str
    slug: str
    excerpt: str
    content: str
    created_at: datetime
    updated_at: datetime
    author: UserAuthor
    tags: list[TagRead]
    like_count: int
    liked_by_current_user: bool


class PostPage(BaseModel):
    items: list[PostRead]
    page: int
    limit: int
    total: int
    total_pages: int


class LikeResponse(BaseModel):
    liked: bool
    like_count: int
