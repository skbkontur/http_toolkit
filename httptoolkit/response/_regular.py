from typing import Any, Callable, Optional

from ._base import BaseResponse


class Response(BaseResponse):
    @property
    def content(self) -> bytes:
        return self._response.content

    @property
    def text(self) -> str:
        return self._response.text

    def json(
        self,
        object_hook: Optional[Callable] = None,
        parse_float: Optional[Callable] = None,
        parse_int: Optional[Callable] = None,
        parse_constant: Optional[Callable] = None,
        object_pairs_hook: Optional[Callable] = None,
    ) -> Any:
        return self._response.json(
            object_hook=object_hook,
            parse_float=parse_float,
            parse_int=parse_int,
            parse_constant=parse_constant,
            object_pairs_hook=object_pairs_hook,
        )
