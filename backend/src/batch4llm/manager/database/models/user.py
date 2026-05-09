from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import Text, ForeignKey, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from batch4llm.manager.database.base import Base

if TYPE_CHECKING:
    from .group import Group


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=True)
    is_supervisor: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    hashed_password_reset_token: Mapped[str] = mapped_column(Text, nullable=True)
    password_reset_timestamp: Mapped[datetime] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=func.now())
    group: Mapped["Group"] = relationship(back_populates="users")

    def to_dict_internal(self):
        return {c.key: getattr(self, c.key) for c in self.__mapper__.columns}

    def to_dict_public(self):
        data = self.to_dict_internal()
        data.pop("password_hash", None)
        data.pop("hashed_password_reset_token", None)
        data.pop("password_reset_timestamp", None)
        return data
