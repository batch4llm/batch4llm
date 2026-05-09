from dataclasses import dataclass


@dataclass
class MediaFile:
    data: bytes
    name: str
    mime_type: str
