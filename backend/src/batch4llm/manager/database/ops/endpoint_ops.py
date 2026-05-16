from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from batch4llm.core.exceptions import NameAlreadyExistsError
from batch4llm.manager.database.models.endpoint import Endpoint
from batch4llm.manager.database.ops.user_ops import get_group_id_subquery


class EndpointOps:
    def __init__(self, session_local: sessionmaker):
        self.SessionLocal = session_local

    def add(
        self, name: str, client: str, provider: str, user_id: int, url=None, token=None
    ):
        with self.SessionLocal() as session:
            subq = get_group_id_subquery(session, user_id)
            ep = Endpoint(
                name=name,
                client=client,
                provider=provider,
                url=url,
                token=token,
                user_id=user_id,
                group_id=subq,
            )
            session.add(ep)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                raise NameAlreadyExistsError(name)
            return ep.to_dict_public()

    def get(self, endpoint_id: int, user_id: int, show_api=False):
        with self.SessionLocal() as session:
            query = session.query(Endpoint).filter_by(id=endpoint_id)
            ep = Endpoint.accessible_by(query, user_id).first()
            if not ep:
                raise ValueError(f"Endpoint ID '{endpoint_id}' not found.")
            if show_api:
                return ep.to_dict_internal()
            else:
                return ep.to_dict_public()

    def list(self, user_id: int, archived: bool | None = None):
        with self.SessionLocal() as session:
            query = Endpoint.accessible_by(session.query(Endpoint), user_id)
            query = Endpoint.filter_archived(query, archived)
            return [e.to_dict_public() for e in query.all()]

    def set_archived(self, endpoint_id: int, user_id: int, archived: bool) -> dict:
        with self.SessionLocal() as session:
            query = session.query(Endpoint).filter_by(id=endpoint_id)
            ep = Endpoint.accessible_by(query, user_id).first()
            if not ep:
                raise ValueError(f"Endpoint ID '{endpoint_id}' not found.")
            ep.archived_at = func.now() if archived else None
            session.commit()
            session.refresh(ep)
            return ep.to_dict_public()

    def delete(self, endpoint_id: int, user_id: int):
        with self.SessionLocal() as session:
            query = session.query(Endpoint).filter_by(id=endpoint_id)
            ep = Endpoint.accessible_by(query, user_id).first()

            if not ep:
                raise ValueError(f"Endpoint ID '{endpoint_id}' not found.")
            session.delete(ep)
            session.commit()
            return ep.to_dict_public()
