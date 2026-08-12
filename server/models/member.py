from sqlalchemy import String, Enum, DateTime, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from database.connection import Base
from datetime import datetime, timezone

class MemberModel(Base):
    __tablename__ = "member"

    nickname: Mapped[str] = mapped_column(
        String(50), 
        primary_key=True
    )
    pwd: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(100),
        nullable=True
    )
    ridingStyles: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=True
    )
    agreeMarketing : Mapped[bool] = mapped_column(
        Boolean,
        nullable=True
    )
    agreeRequired : Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
