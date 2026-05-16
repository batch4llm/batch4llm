from typing import Optional, List
from fastapi import UploadFile
from ..manager.file_manager import FileManager
from ..manager.database import Database


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

    def delete_file(self, file_id: int, user_id: int) -> dict:
        deleted = self.file_manager.delete(file_id, user_id)
        if not deleted:
            raise FileNotFoundError(f"File '{file_id}' not found")
        return {"filename": file_id, "status": "deleted"}

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
