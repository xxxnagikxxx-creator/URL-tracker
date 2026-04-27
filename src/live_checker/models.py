from datetime import datetime, timezone
from typing import List
from sqlalchemy import BigInteger, DateTime, String, ForeignKey, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base
from src.telegram_auth.models import User  
class Link(Base):
    __tablename__ = "links"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String, nullable=False)
    telegram_id: Mapped[int] = mapped_column(ForeignKey("users.telegram_id"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="links")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),  default=lambda: datetime.now(timezone.utc))

    checks: Mapped[List["LinkCheck"]] = relationship("LinkCheck", back_populates="link", cascade="all, delete-orphan")
    
    def to_dict(self) -> dict:
        base_dict = {
            "id": self.id,
            "url": self.url,
            "telegram_id": self.telegram_id,
            "created_at": self.created_at
        }
        if "checks" in self.__dict__:
            base_dict["checks"] = [check.to_dict() for check in self.checks]
        else:
            base_dict["checks"] = []
        return base_dict

class LinkCheck(Base):
    __tablename__ = "link_checks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    link_id: Mapped[int] = mapped_column(ForeignKey("links.id"), nullable=False)
    link: Mapped["Link"] = relationship("Link", back_populates="checks")

    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    response_time: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),  default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "link_id": self.link_id,
            "status_code": self.status_code,
            "response_time": self.response_time,
            "created_at": self.created_at
        }