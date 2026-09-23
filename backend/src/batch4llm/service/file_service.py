from typing import Optional, List
from fastapi import UploadFile
from ..manager.file_manager import FileManager
from ..manager.database import Database
from ..core.exceptions import ResourceInUseError


class FileService:
    def __init__(self, db: Database, file_manager: FileManager):
        self.db = db
        self.file_manager = file_manager

    def upload_file(
        self, file: UploadFile, tags: Optional[List[str]], user_id: int
    ) -> dict:
        return self.file_manager.upload(file, tags, user_id)

    def list_files(self, user_id: int, archived: bool | None = None) -> list[dict]:
        return self.db.files.list(user_id, archived)

    def set_file_archived(self, file_id: int, user_id: int, archived: bool) -> dict:
        return self.db.files.set_archived(file_id, user_id, archived)

    def set_file_tags(self, file_id: int, user_id: int, tags: List[str]) -> dict:
        return self.db.files.set_tags(file_id, user_id, tags)

    def delete_file(self, file_id: int, user_id: int) -> dict:
        deleted = self.file_manager.delete(file_id, user_id)
        if not deleted:
            raise FileNotFoundError(f"File '{file_id}' not found")
        return {"filename": file_id, "status": "deleted"}

    def delete_files_by_tag(self, tag: str, user_id: int) -> dict:
        matching = [f for f in self.list_files(user_id) if tag in (f.get("tags") or [])]

        deleted: List[int] = []
        skipped: List[int] = []
        for f in matching:
            try:
                self.file_manager.delete(f["id"], user_id)
                deleted.append(f["id"])
            except ResourceInUseError:
                skipped.append(f["id"])

        return {"deleted": deleted, "skipped": skipped}

    def get_file_path(self, file_id: int, user_id: int) -> str:
        file_record = self.db.files.get(file_id, user_id)
        if not file_record:
            raise FileNotFoundError(f"File '{file_id}' not found")
        return file_record.path

    def get_file_url(self, file_id: int, user_id: int) -> str:
        try:
            return self.file_manager.get_file_url(file_id, user_id)
        except ValueError as e:
            raise FileNotFoundError(str(e))
