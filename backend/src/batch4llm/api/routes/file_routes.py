from fastapi import APIRouter, HTTPException, status, Security
from fastapi.responses import Response

from batch4llm.service.file_service import FileService
from batch4llm.api.models.file_models import FileData
from fastapi import UploadFile, File, Form
from typing import Optional, List


from batch4llm.core.exceptions import ResourceInUseError
from batch4llm.service.jwt_authenticator import JWTAuthenticator


def build_file_router(file_service: FileService, jwt_authenticator: JWTAuthenticator):
    router = APIRouter(prefix="/files", tags=["Files"])

    @router.post("/upload", response_model=FileData)
    def upload_file(
        file: UploadFile = File(...),
        tags: Optional[List[str]] = Form(None),
        user=Security(jwt_authenticator),
    ):
        return FileData(**file_service.upload_file(file, tags, user["id"]))

    @router.get("/{file_id}/url")
    def get_file_url(file_id: int, user=Security(jwt_authenticator)):
        try:
            url = file_service.get_file_url(file_id, user["id"])
            return {"url": url}
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
            )

    @router.patch("/{file_id}/archive", response_model=FileData)
    def set_file_archived(
        file_id: int, archived: bool = True, user=Security(jwt_authenticator)
    ):
        try:
            return file_service.set_file_archived(file_id, user["id"], archived)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    @router.delete("/delete/{file_id}")
    def delete_file(file_id: int, user=Security(jwt_authenticator)):
        try:
            file_service.delete_file(file_id, user["id"])
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        except ResourceInUseError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        except (FileNotFoundError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
            )

    @router.get("/", response_model=list[FileData])
    def list_files(archived: bool | None = None, user=Security(jwt_authenticator)):
        return file_service.list_files(user["id"], archived)

    @router.get("/tags", response_model=list[str])
    def get_file_tags(user=Security(jwt_authenticator)):
        files = file_service.list_files(user["id"])

        tags = set()
        for f in files:
            if f.get("tags"):
                tags.update(f["tags"])

        return sorted(tags)

    @router.get("/by-tag/{tag}", response_model=list[FileData])
    def get_files_by_tag(tag: str, user=Security(jwt_authenticator)):
        files = file_service.list_files(user["id"])

        return [FileData(**f) for f in files if f.get("tags") and tag in f["tags"]]

    return router
