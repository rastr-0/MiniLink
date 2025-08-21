from pydantic import BaseModel, HttpUrl, Field, ConfigDict, constr
from datetime import datetime


class ShortenRequest(BaseModel):
    original_url: HttpUrl = Field(
        description="URL that will be shortened"
    )
    single_use: bool = Field(
        description="Whether generated alias can be used more than one time",
        default=False
    )
    # regex matches that given alias contains only alphanumeric symbols or dashes
    custom_alias: constr(pattern=r'^[a-zA-Z0-9-_]+$', min_length=5, max_length=20) | None = Field(
        description="optional custom alias for a given URL",
        default=None
    )
    expiration_time: datetime | None = Field(
        description="Optional expiration time. If not set, defaults to 3 hours from creation",
        default=None
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "original_url": "https://www.google.com",
                    "single_use": False,  # defualt value
                    "custom_alias": "search",
                    "expiration_time": None  # default value
                }
            ]
        }
    )


class ShortenResponse(BaseModel):
    short_url: HttpUrl = Field(
        description="Generated short link"
    )
    short_code: str = Field(
        description="Custom or generated alias"
    )
    created_at: datetime = Field(
        description="Creation time of the link"
    )
    expiration_time: datetime | None = Field(
        description="Optional expiration time. If not set, defaults to 3 hours from creation",
        default=None
    )
    created_by_user: str = Field(
        description="Username of the user that generated link"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "short_url": "https://minilink/search",
                    "created_at": "2025:07:31T11:26",
                    "expiration_time": "2025:07:31T14:26",
                    "created_by_user": "123"
                }
            ]
        }
    )


class ShortResponseList(BaseModel):
    short_urls: list[ShortenResponse] = Field()


class StatsResponse(BaseModel):
    original_url: str
    clicks: int


class UserBase(BaseModel):
    """Base model for user related operations"""
    username: str | None = None
    fullname: str | None = None


class UserRequest(UserBase):
    username: str
    fullname: str
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime


class UserUpdate(UserBase):
    """Derived from UserBase without changing, because all the fields are already optional"""
    pass


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str


class LinkFilters(BaseModel):
    """Filter model for GET endpoint"""
    limit: int = 10
    offset: int = 0
    max_clicks: int | None = None
    min_clicks: int | None = None
    active: bool | None = None
    one_time_only: bool | None = None
    created_after: datetime | None = None
    created_before: datetime | None = None
