from .base import BaseParser


class PlainTextParser(BaseParser):
    def parse(self, file_bytes: bytes) -> str:
        self.check_size(file_bytes)
        try:
            return file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return file_bytes.decode("latin-1", errors="replace")
