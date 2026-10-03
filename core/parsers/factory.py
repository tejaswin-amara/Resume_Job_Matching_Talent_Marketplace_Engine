from .base import BaseParser
from .docx_parser import DocxParser
from .pdf_parser import PDFParser
from .text_parser import PlainTextParser


class ParserFactory:
    @staticmethod
    def from_content_type(content_type: str, file_bytes: bytes) -> BaseParser:
        if content_type == "application/pdf" or file_bytes.startswith(b"\x25\x50\x44\x46"):
            return PDFParser()
        elif content_type in [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword",
        ] or file_bytes.startswith(b"PK\x03\x04"):
            return DocxParser()
        elif content_type.startswith("text/"):
            return PlainTextParser()

        # Fallback based on magic bytes if content_type is generic
        if file_bytes.startswith(b"\x25\x50\x44\x46"):
            return PDFParser()
        if file_bytes.startswith(b"PK\x03\x04"):
            return DocxParser()

        return PlainTextParser()
