from typing import Protocol, Iterable, BinaryIO


class BaseFileReader(Protocol):
    """Common interface for all file readers."""

    base_name: str
    modes: Iterable[str]
    default_mode: str

    def read(self, file: BinaryIO, mode: str) -> str: ...
