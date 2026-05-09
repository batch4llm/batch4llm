import re
from typing import BinaryIO

import pymupdf
from batch4llm.manager.file_reader.base import BaseFileReader


class PyMuPDFFileReader(BaseFileReader):
    base_name = "pymupdf"

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
        text = ""
        doc = pymupdf.open(stream=file, filetype="pdf")
        for page in doc:
            text += page.get_text()
        return text

    def _remove_urls(self, text: str) -> str:
        return re.sub(r"https?://\S+|www\.\S+", "", text)
