from sqlite3 import IntegrityError
from sqlalchemy.orm import sessionmaker

from batch4llm.core.exceptions import NameAlreadyExistsError
from batch4llm.manager.database.models.group import Group


class GroupOps:
    def __init__(self, session_local: sessionmaker):
        self.SessionLocal = session_local

    def add_group(self, group_name: str) -> dict:
        with self.SessionLocal() as session:
            group = Group(name=group_name)
            session.add(group)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                raise NameAlreadyExistsError(group_name)
            return group.to_dict()

    def list(self):
        with self.SessionLocal() as session:
            return [e.to_dict() for e in session.query(Group).all()]
