from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Tuple, Iterator

from httptoolkit.request import Request
from httptoolkit.response import Response, StreamResponse
from httptoolkit.sent_request import SentRequest


class BaseTransport(ABC):
    @abstractmethod
    def send(self, request: Request) -> Tuple[SentRequest, Response]:  # pragma: no cover
        pass

    @abstractmethod
    @contextmanager
    def stream(self, request: Request) -> Iterator[Tuple[SentRequest, StreamResponse]]:  # pragma: no cover
        pass
