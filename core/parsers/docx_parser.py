import io

from docx import Document

from .base import BaseParser


class DocxParser(BaseParser):
    MAGIC_BYTES = b"PK\x03\x04"

    def parse(self, file_bytes: bytes) -> str:
        self.check_size(file_bytes)
        if not file_bytes.startswith(self.MAGIC_BYTES):
            raise ValueError("Invalid DOCX magic bytes")

        doc = Document(io.BytesIO(file_bytes))
        return "\n".join([p.text for p in doc.paragraphs])
