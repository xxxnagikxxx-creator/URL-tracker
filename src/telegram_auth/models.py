from sqlalchemy import BigInteger, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from src.database import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)

    username: Mapped[str | None] = mapped_column(String)
    first_name: Mapped[str | None] = mapped_column(String)
    last_name: Mapped[str | None] = mapped_column(String)
    photo_url: Mapped[str | None] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc)
    )

    links: Mapped[list["Link"]] = relationship("Link", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return (f"User(id={self.id}, "
                f"telegram_id={self.telegram_id}, "
                f"username={self.username}, "
                f"first_name={self.first_name}, "
                f"last_name={self.last_name}, "
                f"photo_url={self.photo_url}, "
                f"created_at={self.created_at}, "
                f"updated_at={self.updated_at})")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "telegram_id": self.telegram_id,
            "username": self.username or "",
            "first_name": self.first_name or "",
            "last_name": self.last_name or "",
            "photo_url": self.photo_url or "",
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

