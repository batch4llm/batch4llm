from datetime import datetime

from sqlalchemy import Float, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from batch4llm.manager.database.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .endpoint import Endpoint


class EndpointModel(Base):
    __tablename__ = "endpoint_models"
    __table_args__ = (
        UniqueConstraint("endpoint_id", "model_name", name="uq_endpoint_model"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    endpoint_id: Mapped[int] = mapped_column(
        ForeignKey("endpoints.id", ondelete="CASCADE"), nullable=False
    )
    model_name: Mapped[str] = mapped_column(nullable=False)
    input_cost_per_1m_tokens: Mapped[float | None] = mapped_column(Float, nullable=True)
    output_cost_per_1m_tokens: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=func.now(), onupdate=func.now()
    )

    endpoint: Mapped["Endpoint"] = relationship()

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__mapper__.columns}
