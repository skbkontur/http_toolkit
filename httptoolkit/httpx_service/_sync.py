from typing import Tuple

from httptoolkit import Header
from httptoolkit.service import Service
from httptoolkit.transport import HttpxTransport


class HttpxService(Service):
    def __init__(
        self,
        url: str,
        headers: Tuple[Header, ...] = (),
    ) -> None:
        super().__init__(transport=HttpxTransport(url), headers=headers)
