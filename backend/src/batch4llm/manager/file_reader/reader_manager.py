from typing import Dict, Tuple, Type, BinaryIO
from batch4llm.manager.file_reader.base import BaseFileReader
from batch4llm.manager.file_reader.pymupdf_reader import PyMuPDFFileReader


class FileReaderManager:
    """Registry-based manager for file readers."""

    _readers: Dict[str, Tuple[Type[BaseFileReader], str]] = {}

    @classmethod
    def register(cls, reader_cls: Type[BaseFileReader]):
        for mode in reader_cls.modes:
            public_name = f"{reader_cls.base_name}_{mode}".lower()
            cls._readers[public_name] = (reader_cls, mode)

    @classmethod
    def get_supported(cls):
        reader_list = list(cls._readers.keys())
        reader_list.append("upload")
        return reader_list

    @classmethod
    def read(cls, reader_name: str, file: BinaryIO) -> str:
        reader_name = reader_name.lower()

        if reader_name not in cls._readers:
            raise ValueError(f"Unknown file reader: {reader_name}")

        reader_cls, mode = cls._readers[reader_name]
        return reader_cls().read(file, mode)


# register default readers
FileReaderManager.register(PyMuPDFFileReader)
