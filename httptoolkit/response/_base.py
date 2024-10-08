from datetime import timedelta
from typing import MutableMapping, Optional, Any, Iterator, AsyncIterator, Protocol, Callable


class OriginalResponse(Protocol):
    @property
    def is_success(self) -> bool:
        pass  # pragma: no cover

    @property
    def status_code(self) -> int:
        pass  # pragma: no cover

    @property
    def reason_phrase(self) -> str:
        pass  # pragma: no cover

    @property
    def headers(self) -> MutableMapping[str, str]:
        pass  # pragma: no cover

    @property
    def elapsed(self) -> timedelta:
        pass  # pragma: no cover

    @property
    def content(self) -> bytes:
        pass  # pragma: no cover

    @property
    def text(self) -> str:
        pass  # pragma: no cover

    def json(
        self,
        object_hook: Optional[Callable] = None,
        parse_float: Optional[Callable] = None,
        parse_int: Optional[Callable] = None,
        parse_constant: Optional[Callable] = None,
        object_pairs_hook: Optional[Callable] = None,
    ) -> Any:
        pass  # pragma: no cover

    def iter_bytes(self, chunk_size: Optional[int] = None) -> Iterator[bytes]:
        pass  # pragma: no cover

    def iter_text(self, chunk_size: Optional[int] = None) -> Iterator[str]:
        pass  # pragma: no cover

    def iter_lines(self) -> Iterator[str]:
        pass  # pragma: no cover

    def iter_raw(self, chunk_size: Optional[int] = None) -> Iterator[bytes]:
        pass  # pragma: no cover

    def read(self) -> bytes:
        pass  # pragma: no cover

    def aiter_bytes(self, chunk_size: Optional[int] = None) -> AsyncIterator[bytes]:
        pass  # pragma: no cover

    def aiter_text(self, chunk_size: Optional[int] = None) -> AsyncIterator[str]:
        pass  # pragma: no cover

    def aiter_lines(self) -> AsyncIterator[str]:
        pass  # pragma: no cover

    def aiter_raw(self, chunk_size: Optional[int] = None) -> AsyncIterator[bytes]:
        pass  # pragma: no cover

    async def aread(self) -> bytes:
        pass  # pragma: no cover


class BaseResponse:
    def __init__(self, response: OriginalResponse) -> None:
        self._response = response

    @property
    def ok(self) -> bool:
        return self._response.is_success

    @property
    def status_code(self) -> int:
        return self._response.status_code

    @property
    def reason(self) -> str:
        return self._response.reason_phrase

    @property
    def headers(self) -> MutableMapping[str, str]:
        return self._response.headers

    @property
    def elapsed(self) -> timedelta:
        return self._response.elapsed
