from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import (DeclarativeBase, mapped_column, Mapped, relationship)


class Base(DeclarativeBase):
    pass


class ShortURL(Base):
    __tablename__ = "short_urls"

    id: Mapped[int] = mapped_column(primary_key=True)
    long_url: Mapped[str] = mapped_column(String)
    short_url: Mapped[str] = mapped_column(String(10))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    clicks: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[str] = mapped_column(String)
    user: Mapped["User"] = relationship(back_populates="short_urls")

    def __repr__(self):
        return (f"Link (id: {self.id}, long_url: {self.long_url}, "
                f"short_url: {self.short_url}, created_at: {self.created_at})")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True)
    fullname: Mapped[str] = mapped_column(String)
    hasshed_password: Mapped[str] = mapped_column(String)

    short_urls: Mapped[list["ShortURL"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"Link (id: {self.id}, username: {self.username}, fullname: {self.fullname})"
