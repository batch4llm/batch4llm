from ..manager.database import Database


class ModelService:
    def __init__(self, db: Database):
        self.db = db

    def list_models(self, user_id: int) -> list[dict]:
        return self.db.endpoint_models.list_all(user_id)
