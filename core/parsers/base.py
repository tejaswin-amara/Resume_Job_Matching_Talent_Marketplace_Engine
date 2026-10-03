from abc import ABC, abstractmethod


class BaseParser(ABC):
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

    @abstractmethod
    def parse(self, file_bytes: bytes) -> str:
        pass

    def check_size(self, file_bytes: bytes):
        if len(file_bytes) > self.MAX_FILE_SIZE:
            raise ValueError(f"File size exceeds {self.MAX_FILE_SIZE} bytes")
