from sqlalchemy.orm import Mapped, mapped_column

from batch4llm.manager.database.base import Base
from .resource_mixin import ResourceMixin


class Prompt(Base, ResourceMixin):
    __tablename__ = "prompts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    multi_prompt: Mapped[bool] = mapped_column(nullable=False, default=False)

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__mapper__.columns}
