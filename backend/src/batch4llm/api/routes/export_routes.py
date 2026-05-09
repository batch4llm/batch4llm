from fastapi import Query, Security
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from batch4llm.service.export_service import ExportService
from batch4llm.service.jwt_authenticator import JWTAuthenticator


def build_export_router(
    export_service: ExportService, jwt_authenticator: JWTAuthenticator
):
    router = APIRouter(prefix="/export", tags=["Export"])

    @router.get("/batches")
    def export_csv(
        mode: str, batch_ids: list[int] = Query(), user=Security(jwt_authenticator)
    ):
        file_buffer, filename, content_type = export_service.export_batches(
            batch_ids, mode, user["id"]
        )
        return StreamingResponse(
            file_buffer,
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    return router
