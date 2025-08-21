from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import (DeclarativeBase, mapped_column, Mapped, relationship)
from datetime import datetime


class Base(DeclarativeBase):
    pass


class ShortURL(Base):
    __tablename__ = "short_urls"

    id: Mapped[int] = mapped_column(primary_key=True)
    long_url: Mapped[str] = mapped_column(String(2048))
    short_code: Mapped[str] = mapped_column(String, unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    clicks: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expiration_time: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)

    user: Mapped["User"] = relationship(back_populates="short_urls")

    def __repr__(self):
        return (f"Link (id: {self.id}, long_url: {self.long_url}, "
                f"short_code: {self.short_code}, created_at: {self.created_at})")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True)
    fullname: Mapped[str] = mapped_column(String)
    hasshed_password: Mapped[str] = mapped_column(String)

    short_urls: Mapped[list["ShortURL"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"Link (id: {self.id}, username: {self.username}, fullname: {self.fullname})"
