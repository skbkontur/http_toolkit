from contextlib import contextmanager
from typing import Iterator, Tuple

from httptoolkit.request import Request
from httptoolkit.response import Response, StreamResponse
from httptoolkit.transport._httpx._session._sync import HttpxSession

from httptoolkit.sent_request import SentRequest
from ._base import BaseHttpxTransport
from httptoolkit.transport import BaseTransport


class HttpxTransport(BaseTransport, BaseHttpxTransport):
    _session_class = HttpxSession

    def send(self, request: Request) -> Tuple[SentRequest, Response]:
        httpx_request = self._build_httpx_request(request)
        sent_request = self._prepare_sent_request(request, httpx_request)
        with self._managed_session(sent_request) as session:
            return sent_request, Response(session.send(httpx_request))

    @contextmanager
    def stream(self, request: Request) -> Iterator[Tuple[SentRequest, StreamResponse]]:
        httpx_request = self._build_httpx_request(request)
        sent_request = self._prepare_sent_request(request, httpx_request)
        with self._managed_session(sent_request) as session:
            with session.stream(httpx_request) as response:
                yield sent_request, StreamResponse(response)
