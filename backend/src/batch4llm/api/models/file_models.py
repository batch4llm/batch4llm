from datetime import datetime
from pydantic import BaseModel


class FileData(BaseModel):
    id: int
    name: str
    size: int | None
    mime_type: str | None
    tags: list[str] | None = None
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None = None
