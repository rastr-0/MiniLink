from pydantic import BaseModel, HttpUrl
from datetime import datetime


class ShortenRequest(BaseModel):
    url: HttpUrl


class ShortenResponse(BaseModel):
    short_url: str


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
