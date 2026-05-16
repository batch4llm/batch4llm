from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import or_, select
from .user import User


class ResourceMixin:
    user_id: Mapped[int] = mapped_column(nullable=False)
    group_id: Mapped[int] = mapped_column(nullable=True)
    archived_at: Mapped[datetime | None] = mapped_column(nullable=True, default=None)

    @classmethod
    def accessible_by(cls, query, user_id: int):
        user_group_subq = (
            select(User.group_id).where(User.id == user_id).scalar_subquery()
        )
        return query.filter(
            or_(cls.user_id == user_id, cls.group_id == user_group_subq)
        )

    @classmethod
    def filter_archived(cls, query, archived: bool | None):
        if archived is True:
            return query.filter(cls.archived_at.isnot(None))
        if archived is False:
            return query.filter(cls.archived_at.is_(None))
        return query
