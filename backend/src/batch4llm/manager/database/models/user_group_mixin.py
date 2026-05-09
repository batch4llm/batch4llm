from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import or_, select
from .user import User


class UserGroupMixin:
    user_id: Mapped[int] = mapped_column(nullable=False)
    group_id: Mapped[int] = mapped_column(nullable=True)

    @classmethod
    def accessible_by(cls, query, user_id: int):
        user_group_subq = (
            select(User.group_id).where(User.id == user_id).scalar_subquery()
        )

        return query.filter(
            or_(cls.user_id == user_id, cls.group_id == user_group_subq)
        )
