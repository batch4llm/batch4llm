from sqlalchemy.orm import sessionmaker

from batch4llm.manager.database.models.endpoint import Endpoint
from batch4llm.manager.database.models.endpoint_model import EndpointModel


class EndpointModelOps:
    def __init__(self, session_local: sessionmaker):
        self.SessionLocal = session_local

    def upsert(
        self,
        endpoint_id: int,
        model_name: str,
        input_cost_per_1m_tokens: float | None,
        output_cost_per_1m_tokens: float | None,
    ):
        with self.SessionLocal() as session:
            model = (
                session.query(EndpointModel)
                .filter_by(endpoint_id=endpoint_id, model_name=model_name)
                .first()
            )
            if model:
                model.input_cost_per_1m_tokens = input_cost_per_1m_tokens
                model.output_cost_per_1m_tokens = output_cost_per_1m_tokens
            else:
                model = EndpointModel(
                    endpoint_id=endpoint_id,
                    model_name=model_name,
                    input_cost_per_1m_tokens=input_cost_per_1m_tokens,
                    output_cost_per_1m_tokens=output_cost_per_1m_tokens,
                )
                session.add(model)
            session.commit()

    def list_all(self, user_id: int) -> list[dict]:
        with self.SessionLocal() as session:
            query = session.query(EndpointModel).join(
                Endpoint, EndpointModel.endpoint_id == Endpoint.id
            )
            query = Endpoint.accessible_by(query, user_id)
            results = []
            for model in query.all():
                data = model.to_dict()
                data["endpoint_name"] = model.endpoint.name
                data["provider"] = model.endpoint.provider
                results.append(data)
            return results
