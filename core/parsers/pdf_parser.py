import io

from pypdf import PdfReader

from .base import BaseParser


class PDFParser(BaseParser):
    MAGIC_BYTES = b"\x25\x50\x44\x46"

    def parse(self, file_bytes: bytes) -> str:
        self.check_size(file_bytes)
        if not file_bytes.startswith(self.MAGIC_BYTES):
            raise ValueError("Invalid PDF magic bytes")

        reader = PdfReader(io.BytesIO(file_bytes))
        text = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)

        full_text = "\n".join(text)
        if len(full_text) > 500000:  # Decompression bomb guard
            raise ValueError("Extracted text is too large")

        return full_text
