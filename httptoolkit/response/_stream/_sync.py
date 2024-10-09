from typing import Optional, Iterator

from .._base import BaseResponse


class StreamResponse(BaseResponse):
    def iter_bytes(self, chunk_size: Optional[int] = None) -> Iterator[bytes]:
        return self._response.iter_bytes(chunk_size)

    def iter_text(self, chunk_size: Optional[int] = None) -> Iterator[str]:
        return self._response.iter_text(chunk_size)

    def iter_lines(self) -> Iterator[str]:
        return self._response.iter_lines()

    def iter_raw(self, chunk_size: Optional[int] = None) -> Iterator[bytes]:
        return self._response.iter_raw(chunk_size)

    def read(self) -> bytes:
        return self._response.read()

    @property
    def text(self) -> str:
        return self._response.text
