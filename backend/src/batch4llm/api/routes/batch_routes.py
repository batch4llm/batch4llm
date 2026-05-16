from fastapi import APIRouter, HTTPException, status, Security

from batch4llm.api.models.batch_models import BatchData, BatchRunRequest, BatchFileData
from batch4llm.service.jwt_authenticator import JWTAuthenticator
from batch4llm.service.batch_service import BatchService


def build_batch_router(
    batch_service: BatchService, jwt_authenticator: JWTAuthenticator
):
    router = APIRouter(prefix="/batches", tags=["Batches"])

    @router.post("/start", response_model=BatchData)
    def start_run(request: BatchRunRequest, user=Security(jwt_authenticator)):

        result = batch_service.start(
            prompt_id=request.prompt_id,
            endpoint_id=request.endpoint_id,
            files=request.files,
            file_reader=request.file_reader,
            model=request.model,
            temperature=request.temperature,
            user_id=user["id"],
            json_format=request.json_format,
            batch_worker_settings=request.batch_worker_settings,
            use_provider_batch=request.use_provider_batch,
        )
        return BatchData(**result)

    @router.post("/stop/{batch_id}")
    def stop_run(batch_id: int, user=Security(jwt_authenticator)):
        try:
            result = batch_service.stop(batch_id, user["id"])
            return BatchData(**result)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    @router.get("/{batch_id}", response_model=BatchData)
    def get_batch(batch_id: int, user=Security(jwt_authenticator)):
        result = batch_service.get_batch(batch_id, user["id"])
        return BatchData(**result)

    @router.get("/files/{batch_id}", response_model=list[BatchFileData])
    def get_batch_files(batch_id: int, user=Security(jwt_authenticator)):
        return batch_service.get_batch_files(batch_id, user["id"])

    @router.get("/log/{batch_id}")
    def get_batch_log(
        batch_id: int, after_id: int = None, user=Security(jwt_authenticator)
    ):
        return batch_service.get_batch_log(batch_id, user["id"], after_id)

    @router.get("/", response_model=list[BatchData])
    def list_runs(archived: bool | None = None, user=Security(jwt_authenticator)):
        return batch_service.list_batches(user["id"], archived)

    @router.patch("/{batch_id}/archive", response_model=BatchData)
    def archive_batch(batch_id: int, user=Security(jwt_authenticator)):
        try:
            return batch_service.archive_batch(batch_id, user["id"])
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return router
