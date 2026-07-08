from .base import get_session
from batch4llm.manager.database.models.user import User as User
from batch4llm.manager.database.models.group import Group as Group
from batch4llm.manager.database.ops.endpoint_ops import EndpointOps
from batch4llm.manager.database.ops.endpoint_model_ops import EndpointModelOps
from batch4llm.manager.database.ops.batch_ops import BatchOps
from batch4llm.manager.database.ops.file_ops import FileOps
from batch4llm.manager.database.ops.prompt_ops import PromptOps
from batch4llm.manager.database.ops.user_ops import UserOps
from batch4llm.manager.database.ops.group_ops import GroupOps
from batch4llm.manager.database.ops.worker_ops import WorkerOps
from batch4llm.manager.database.ops.export_ops import ExportOps


class Database:
    batches: BatchOps
    endpoints: EndpointOps
    endpoint_models: EndpointModelOps
    files: FileOps
    prompts: PromptOps
    users: UserOps
    groups: GroupOps
    workers: WorkerOps
    export: ExportOps

    def __init__(self, db_path):
        self.SessionLocal = get_session(str(db_path))
        self.batches = BatchOps(self.SessionLocal)
        self.endpoints = EndpointOps(self.SessionLocal)
        self.endpoint_models = EndpointModelOps(self.SessionLocal)
        self.files = FileOps(self.SessionLocal)
        self.prompts = PromptOps(self.SessionLocal)
        self.users = UserOps(self.SessionLocal)
        self.groups = GroupOps(self.SessionLocal)
        self.worker = WorkerOps(self.SessionLocal)
        self.export = ExportOps(self.SessionLocal)
