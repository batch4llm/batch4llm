from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from batch4llm.manager.database.base import Base

if TYPE_CHECKING:
    from .user import User


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=func.now())

    users: Mapped[list["User"]] = relationship(back_populates="group")

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__mapper__.columns}
