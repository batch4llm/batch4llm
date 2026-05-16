from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func
from datetime import datetime

from batch4llm.manager.database.base import Base
from .resource_mixin import ResourceMixin


class Endpoint(Base, ResourceMixin):
    __tablename__ = "endpoints"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    client: Mapped[str] = mapped_column(nullable=False)
    provider: Mapped[str] = mapped_column(nullable=False)
    url: Mapped[str | None] = mapped_column(nullable=True)
    token: Mapped[str | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=func.now())

    user_id: Mapped[int] = mapped_column(nullable=True)
    group_id: Mapped[int] = mapped_column(nullable=True)

    def to_dict_internal(self):
        return {c.key: getattr(self, c.key) for c in self.__mapper__.columns}

    def to_dict_public(self):
        data = self.to_dict_internal()
        token = data.get("token")
        if token and len(token) > 14:
            data["token"] = f"{token[:3]}............{token[-3:]}"
        elif token and len(token) > 7:
            data["token"] = f"{token[:1]}......{token[-1:]}"
        elif token:
            data["token"] = "......"
        return data
