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
        description="ID of the user that generated link"
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


class StatsResponse(BaseModel):
    original_url: str
    clicks: int


class UserRequest(BaseModel):
    username: str
    fullname: str
    password: str


class UserResponse(BaseModel):
    username: str
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str
