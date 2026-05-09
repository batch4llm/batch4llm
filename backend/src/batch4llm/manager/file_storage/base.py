from abc import ABC, abstractmethod
from datetime import timedelta
from typing import List, BinaryIO


class FileStorage(ABC):
    @abstractmethod
    def upload(self, file_path: str, content: BinaryIO, length: int) -> bool:
        pass

    @abstractmethod
    def download(self, file_path: str) -> BinaryIO:
        pass

    @abstractmethod
    def delete(self, file_path: str) -> bool:
        pass

    @abstractmethod
    def exists(self, file_path: str) -> bool:
        pass

    @abstractmethod
    def list(self, prefix: str = "") -> List[str]:
        pass

    @abstractmethod
    def get_file_url(
        self,
        file_path: str,
        expires: timedelta = timedelta(hours=1),
        mime_type: str | None = None,
    ) -> str:
        pass
