from fastapi import APIRouter
from batch4llm.service.batch_service import BatchService


def build_pipeline_router(batch_service: BatchService):
    router = APIRouter(prefix="/pipeline", tags=["Pipeline"])

    @router.get("/engines", response_model=list[str])
    def list_engines():
        return batch_service.list_engines()

    @router.get("/file_readers", response_model=list[str])
    def list_file_readers():
        return batch_service.list_file_readers()

    return router
