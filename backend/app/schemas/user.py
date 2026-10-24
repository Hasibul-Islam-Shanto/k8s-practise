from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class UserAuthor(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    username: str
    avatar_url: str | None = None


class UserRead(UserAuthor):
    email: str
    bio: str | None = None
    created_at: datetime


class UserProfile(UserAuthor):
    bio: str | None = None
    created_at: datetime
    post_count: int
    total_likes_received: int


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    bio: str | None = Field(default=None, max_length=500)
    avatar_url: str | None = Field(default=None, max_length=512)

    @field_validator("avatar_url")
    @classmethod
    def validate_avatar_url(cls, value: str | None) -> str | None:
        if value is None or value.strip() == "":
            return None
        # Validate the shape but store the plain string.
        HttpUrl(value)
        return value.strip()
