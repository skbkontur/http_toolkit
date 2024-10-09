import time
from contextlib import contextmanager
from typing import Iterator, Optional

from httpx import Client, HTTPTransport
from httpx import Request as OriginalHttpxRequest
from httpx import Response as OriginalHttpxResponse
from httptoolkit.retry import RetryManager


class HttpxSession(Client):
    def __init__(
        self,
        retry_manager: RetryManager,
        allow_unverified_peer: Optional[bool] = False,
        proxies: Optional[dict] = None,
    ) -> None:
        super().__init__(
            transport=HTTPTransport(
                verify=not allow_unverified_peer,
            ),
            proxies=proxies,
        )

        self._retry_manager = retry_manager

    def send(self, request: OriginalHttpxRequest, *args, **kwargs) -> OriginalHttpxResponse:
        for retry in self._retry_manager.get_retries(request.method):
            with retry:
                response = super().send(request, *args, **kwargs)
                retry.process_response(response)
                return response

            # noinspection PyUnreachableCode
            time.sleep(retry.backoff)

    @contextmanager
    def stream(self, request: OriginalHttpxRequest, *args, **kwargs) -> Iterator[OriginalHttpxResponse]:
        kwargs.update(request=request, stream=True)
        response = self.send(*args, **kwargs)
        try:
            yield response
        finally:
            response.close()
