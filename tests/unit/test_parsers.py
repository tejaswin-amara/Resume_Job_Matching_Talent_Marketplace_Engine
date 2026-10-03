import pytest

from core.parsers.base import BaseParser
from core.parsers.text_parser import PlainTextParser

try:
    from core.parsers.docx_parser import DocxParser
    from core.parsers.factory import ParserFactory
    from core.parsers.pdf_parser import PDFParser

    _HAS_PARSER_DEPS = True
except ImportError:
    _HAS_PARSER_DEPS = False

_needs_deps = pytest.mark.skipif(not _HAS_PARSER_DEPS, reason="pypdf/python-docx not installed")


def test_plain_text_parser_extracts_text():
    parser = PlainTextParser()
    res = parser.parse(b"Hello world!")
    assert res == "Hello world!"


def test_plain_text_parser_handles_empty():
    parser = PlainTextParser()
    res = parser.parse(b"")
    assert res == ""


@_needs_deps
def test_pdf_parser_rejects_non_pdf_magic_bytes():
    parser = PDFParser()
    with pytest.raises(ValueError, match="Invalid PDF magic bytes"):
        parser.parse(b"not a pdf")


@_needs_deps
def test_docx_parser_rejects_non_zip_magic_bytes():
    parser = DocxParser()
    with pytest.raises(ValueError, match="Invalid DOCX magic bytes"):
        parser.parse(b"not a zip")


@_needs_deps
def test_parser_factory_selects_correct_parser():
    assert isinstance(
        ParserFactory.from_content_type("application/pdf", b"\x25\x50\x44\x46-1.4"), PDFParser
    )
    assert isinstance(
        ParserFactory.from_content_type(
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            b"PK\x03\x04",
        ),
        DocxParser,
    )
    assert isinstance(ParserFactory.from_content_type("text/plain", b"hello"), PlainTextParser)


def test_file_size_limit_enforcement():
    parser = PlainTextParser()
    big_bytes = b"a" * (BaseParser.MAX_FILE_SIZE + 1)
    with pytest.raises(ValueError, match="File size exceeds"):
        parser.parse(big_bytes)
