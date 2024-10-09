import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

from httpx import AsyncClient, AsyncHTTPTransport
from httpx import Request as OriginalHttpxRequest
from httpx import Response as OriginalHttpxResponse
from httptoolkit.retry import RetryManager


class AsyncHttpxSession(AsyncClient):
    def __init__(
        self,
        retry_manager: RetryManager,
        allow_unverified_peer: Optional[bool] = False,
        proxies: Optional[dict] = None,
    ) -> None:
        super().__init__(
            transport=AsyncHTTPTransport(
                verify=not allow_unverified_peer,
            ),
            proxies=proxies,
        )

        self._retry_manager = retry_manager

    async def send(self, request: OriginalHttpxRequest, *args, **kwargs) -> OriginalHttpxResponse:
        for retry in self._retry_manager.get_retries(request.method):
            with retry:
                response = await super().send(request, *args, **kwargs)
                retry.process_response(response)
                return response

            # noinspection PyUnreachableCode
            await asyncio.sleep(retry.backoff)

    @asynccontextmanager
    async def stream(self, request: OriginalHttpxRequest, *args, **kwargs) -> AsyncIterator[OriginalHttpxResponse]:
        kwargs.update(request=request, stream=True)
        response = await self.send(*args, **kwargs)
        try:
            yield response
        finally:
            await response.aclose()
