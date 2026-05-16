from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from batch4llm.core.exceptions import NameAlreadyExistsError, ResourceInUseError
from batch4llm.manager.database.models.batch import Batch
from batch4llm.manager.database.models.prompt import Prompt
from batch4llm.manager.database.ops.user_ops import get_group_id_subquery


class PromptOps:
    def __init__(self, session_local: sessionmaker):
        self.SessionLocal = session_local

    def add(self, name: str, content: str, multi_prompt: bool, user_id: int) -> dict:
        with self.SessionLocal() as session:
            subq = get_group_id_subquery(session, user_id)

            pr = Prompt(
                name=name,
                content=content,
                multi_prompt=multi_prompt,
                user_id=user_id,
                group_id=subq,
            )
            session.add(pr)
            try:
                session.commit()
                session.refresh(pr)
                return pr.to_dict()
            except IntegrityError:
                session.rollback()
                raise NameAlreadyExistsError(name)

    def list(self, user_id: int, archived: bool | None = None) -> list[dict]:
        with self.SessionLocal() as session:
            query = Prompt.accessible_by(session.query(Prompt), user_id)
            query = Prompt.filter_archived(query, archived)
            return [p.to_dict() for p in query.all()]

    def get(self, prompt_id: int, user_id: int) -> dict | None:
        with self.SessionLocal() as session:
            query = session.query(Prompt).filter_by(id=prompt_id)
            prompt = Prompt.accessible_by(query, user_id).first()
            if prompt:
                return prompt.to_dict()
            return None

    def set_archived(self, prompt_id: int, user_id: int, archived: bool) -> dict:
        with self.SessionLocal() as session:
            query = session.query(Prompt).filter_by(id=prompt_id)
            prompt = Prompt.accessible_by(query, user_id).first()
            if not prompt:
                raise ValueError(f"Prompt id '{prompt_id}' not found.")
            prompt.archived_at = func.now() if archived else None
            session.commit()
            session.refresh(prompt)
            return prompt.to_dict()

    def delete(self, prompt_id: int, user_id: int) -> dict:
        with self.SessionLocal() as session:
            query = session.query(Prompt).filter_by(id=prompt_id)
            prompt = Prompt.accessible_by(query, user_id).first()
            if not prompt:
                raise ValueError(f"Prompt with ID {prompt_id} not found.")
            in_use = session.query(Batch).filter_by(prompt_id=prompt_id).first()
            if in_use:
                raise ResourceInUseError(
                    f"Prompt '{prompt_id}' is still referenced by a batch and cannot be deleted."
                )
            session.delete(prompt)
            session.commit()
            return prompt.to_dict()
