from sqlalchemy import JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from batch4llm.manager.database.base import Base
from .resource_mixin import ResourceMixin


class File(Base, ResourceMixin):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    path: Mapped[str] = mapped_column(nullable=False, unique=True)
    tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    mime_type: Mapped[str | None] = mapped_column(nullable=True)
    size: Mapped[int | None] = mapped_column(nullable=True)
    in_storage: Mapped[bool] = mapped_column(nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=func.now())

    user_id: Mapped[int] = mapped_column(nullable=True)
    group_id: Mapped[int] = mapped_column(nullable=True)

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__mapper__.columns}
