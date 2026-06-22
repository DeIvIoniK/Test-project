from datetime import datetime
from sqlalchemy import BigInteger, Boolean, DateTime, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255))
    first_name: Mapped[str | None] = mapped_column(String(255))
    language: Mapped[str] = mapped_column(String(8), default="ru")
    voice_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    city: Mapped[str | None] = mapped_column(String(255))
    timezone: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DialogueContext(Base):
    __tablename__ = "dialogue_contexts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(index=True)
    summary: Mapped[str] = mapped_column(Text, default="")
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
