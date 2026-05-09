import os
import uuid
from datetime import timedelta

from fastapi import UploadFile
from batch4llm.manager.database import Database
from .media_file import MediaFile
from batch4llm.manager.file_storage import FileStorage


class FileManager:
    def __init__(self, storage: FileStorage, db: Database):
        self.storage = storage
        self.db = db

    def _unique_name(self, original_name: str) -> str:
        base, ext = os.path.splitext(original_name)
        return f"{uuid.uuid4().hex[:8]}{ext}"

    def upload(self, file: UploadFile, tags: list[str], user_id: int):
        unique_name = self._unique_name(file.filename)

        if not self.storage.upload(unique_name, file.file, file.size):
            return None

        file_record = self.db.files.add(
            name=file.filename,
            path=unique_name,
            tags=tags,
            mime_type=file.content_type,
            size=file.size,
            user_id=user_id,
        )

        return file_record

    def download(self, file_id: int, user_id: int) -> MediaFile:
        file_record = self.db.files.get(file_id, user_id)
        if not file_record:
            raise ValueError("File does not exist or user has no permissions!")

        file_path = file_record.path
        binary_io = self.storage.download(file_path)
        return MediaFile(binary_io, file_record.name, file_record.mime_type)

    def download_intern(self, file_id: int) -> MediaFile:
        file_record = self.db.files.get_system_intern(file_id)
        if not file_record:
            raise ValueError("File does not exist!")

        file_path = file_record.path
        binary_io = self.storage.download(file_path)
        return MediaFile(binary_io.read(), file_record.name, file_record.mime_type)

    def get_file_url(
        self, file_id: int, user_id: int, expires: timedelta = timedelta(hours=1)
    ) -> str:
        file_record = self.db.files.get(file_id, user_id)
        if not file_record:
            raise ValueError("File does not exist or user has no permissions!")
        return self.storage.get_file_url(
            file_record.path, expires, mime_type=file_record.mime_type
        )

    def delete(self, file_id: int, user_id: int) -> bool:
        file_record = self.db.files.get(file_id, user_id)
        if not file_record:
            return False

        file_path = file_record.path

        if self.storage.delete(file_path):
            self.db.files.delete(file_id, user_id)
            return True
        return False

    def list(self) -> list[str]:
        return self.storage.list()

    def sync_storage_with_db(self):
        storage_files = self.list()
        db_files = self.db.files.system_list()
        db_paths = {f["path"] for f in db_files}

        # check files in storage; if not in db: add
        for file in storage_files:
            if file not in db_paths:
                # todo: rename file?
                # todo: contenttype und size possible null reference
                self.db.files.add(
                    name=file,
                    path=file,
                    tags=None,
                    mime_type="test",
                    size=0,
                    user_id=0,
                )

        for db_file in db_paths:
            if db_file not in storage_files:
                self.db.files.set_storage_status(path=db_file, in_storage=False)
