import re
from typing import BinaryIO

from PyPDF2 import PdfReader
from batch4llm.manager.file_reader.base import BaseFileReader


class PyPDF2FileReader(BaseFileReader):
    base_name = "pypdf2"

    modes = (
        "default",
        "remove_urls",
    )

    default_mode = "default"

    def read(self, file: BinaryIO, mode: str) -> str:
        text = self._read_pdf(file)

        if mode == "remove_urls":
            text = self._remove_urls(text)

        return text.strip()

    def _read_pdf(self, file: BinaryIO) -> str:
        reader = PdfReader(file)
        return "".join(page.extract_text() or "" for page in reader.pages)

    def _remove_urls(self, text: str) -> str:
        return re.sub(r"https?://\S+|www\.\S+", "", text)
