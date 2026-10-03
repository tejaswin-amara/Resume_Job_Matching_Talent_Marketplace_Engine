from .base import BaseParser
from .text_parser import PlainTextParser

__all__ = ["BaseParser", "PlainTextParser"]


def __getattr__(name: str):
    if name == "PDFParser":
        from .pdf_parser import PDFParser

        return PDFParser
    if name == "DocxParser":
        from .docx_parser import DocxParser

        return DocxParser
    if name == "ParserFactory":
        from .factory import ParserFactory

        return ParserFactory
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
