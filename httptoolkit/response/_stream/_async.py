from typing import Optional, AsyncIterator

from .._base import BaseResponse


class AsyncStreamResponse(BaseResponse):
    def iter_bytes(self, chunk_size: Optional[int] = None) -> AsyncIterator[bytes]:
        return self._response.aiter_bytes(chunk_size)

    def iter_text(self, chunk_size: Optional[int] = None) -> AsyncIterator[str]:
        return self._response.aiter_text(chunk_size)

    def iter_lines(self) -> AsyncIterator[str]:
        return self._response.aiter_lines()

    def iter_raw(self, chunk_size: Optional[int] = None) -> AsyncIterator[bytes]:
        return self._response.aiter_raw(chunk_size)

    @property
    def text(self) -> str:
        return self._response.text

    async def read(self) -> bytes:
        return await self._response.aread()
