from sqlalchemy.orm import sessionmaker
from batch4llm.manager.database.models.user import User


def get_group_id_subquery(session, user_id: int):
    return session.query(User.group_id).filter(User.id == user_id).scalar_subquery()


class UserOps:
    def __init__(self, session_local: sessionmaker):
        self.SessionLocal = session_local

    def add(self, username: str, password_hash: str, is_admin: bool | None = None):
        with self.SessionLocal() as session:
            user_exists = session.query(User).first()
            resolved_admin = is_admin if is_admin is not None else not bool(user_exists)
            user = User(
                username=username, password_hash=password_hash, is_admin=resolved_admin
            )
            session.add(user)
            session.commit()

    def does_any_user_exist(self) -> bool:
        with self.SessionLocal() as session:
            user_exists = session.query(User).first()
            return bool(user_exists)

    def get_for_verification(self, username: str):
        with self.SessionLocal() as session:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                raise ValueError(f"User '{username}' not found.")
            return user.to_dict_internal()

    def get_by_username(self, username: str):
        with self.SessionLocal() as session:
            user = session.query(User).filter_by(username=username).first()
            if user:
                return user.to_dict_public()
            return None

    def list(self):
        with self.SessionLocal() as session:
            return [e.to_dict_public() for e in session.query(User).all()]

    def set_group(self, username: str, group_id: int):
        with self.SessionLocal() as session:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                raise ValueError(f"User '{username}' not found.")
            user.group_id = group_id
            session.commit()
            session.refresh(user)
            return user.to_dict_public()
