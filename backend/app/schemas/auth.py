from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.schemas.user import UserRead

USERNAME_PATTERN = r"^[a-zA-Z0-9_]+$"


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    username: str = Field(min_length=3, max_length=50, pattern=USERNAME_PATTERN)
    email: EmailStr
    # 72 is bcrypt's ceiling, so reject longer rather than silently truncating.
    password: str = Field(min_length=8, max_length=72)
    confirm_password: str | None = None
    bio: str | None = Field(default=None, max_length=500)

    @field_validator("username")
    @classmethod
    def lowercase_username(cls, value: str) -> str:
        return value.lower()

    @model_validator(mode="after")
    def passwords_must_match(self) -> "RegisterRequest":
        if self.confirm_password is not None and self.confirm_password != self.password:
            raise ValueError("Passwords do not match")
        return self


class LoginRequest(BaseModel):
    # Accepts either an email address or a username.
    identifier: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=72)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
