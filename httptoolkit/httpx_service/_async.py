from typing import Tuple

from httptoolkit import Header
from httptoolkit.service import AsyncService
from httptoolkit.transport import AsyncHttpxTransport


class AsyncHttpxService(AsyncService):
    def __init__(
        self,
        url: str,
        headers: Tuple[Header, ...] = (),
    ) -> None:
        super().__init__(transport=AsyncHttpxTransport(url), headers=headers)
