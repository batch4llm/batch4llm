from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from batch4llm.manager.database.models.file import File
from batch4llm.manager.database.ops.user_ops import get_group_id_subquery


class FileOps:
    def __init__(self, session_local: sessionmaker):
        self.SessionLocal = session_local

    def add(
        self,
        path: str,
        name: str,
        tags: list[str],
        mime_type: str,
        size: int,
        user_id: int,
    ):
        with self.SessionLocal() as session:

            subq = get_group_id_subquery(session, user_id)

            file = File(
                path=path,
                name=name,
                tags=tags,
                mime_type=mime_type,
                size=size,
                user_id=user_id,
                group_id=subq,
            )
            session.add(file)
            session.commit()
            return file.to_dict()

    def get(self, file_id: int, user_id: int) -> File:
        with self.SessionLocal() as session:
            query = session.query(File).filter_by(id=file_id)
            file = File.accessible_by(query, user_id).first()
            if not file:
                raise ValueError(f"File with ID '{file_id}' not found.")
            return file

    def get_system_intern(self, file_id: int) -> File:
        with self.SessionLocal() as session:
            file = session.query(File).filter_by(id=file_id).first()
            if not file:
                raise ValueError(f"File with ID '{file_id}' not found.")
            return file

    def list(self, user_id: int, archived: bool | None = None):
        with self.SessionLocal() as session:
            query = File.accessible_by(session.query(File), user_id)
            query = File.filter_archived(query, archived)
            return [f.to_dict() for f in query.all()]

    def system_list(self):
        with self.SessionLocal() as session:
            files = session.query(File).all()
            return [f.to_dict() for f in files]

    def archive(self, file_id: int, user_id: int) -> dict:
        with self.SessionLocal() as session:
            query = session.query(File).filter_by(id=file_id)
            file = File.accessible_by(query, user_id).first()
            if not file:
                raise ValueError(f"File with ID '{file_id}' not found.")
            file.archived_at = func.now()
            session.commit()
            session.refresh(file)
            return file.to_dict()

    def delete(self, file_id: int, user_id: int) -> File:
        with self.SessionLocal() as session:
            query = session.query(File).filter_by(id=file_id)
            file = File.accessible_by(query, user_id).first()
            if not file:
                raise ValueError(f"File with ID '{file_id}' not found.")
            session.delete(file)
            session.commit()
            return file

    def set_storage_status(self, path: str, in_storage: bool):
        with self.SessionLocal() as session:
            file = session.query(File).filter_by(path=path).first()
            if not file:
                raise ValueError(f"File '{path}' not found.")
            file.in_storage = in_storage
            session.commit()
            session.refresh(file)
            return file.to_dict()
