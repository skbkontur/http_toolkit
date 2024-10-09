from contextlib import asynccontextmanager, contextmanager
from typing import Optional, AsyncIterator, Union, Tuple, List, Dict, BinaryIO, Iterator

from httptoolkit.errors import HttpError, TransportError, ServiceError
from httptoolkit.header import Header
from httptoolkit.request import Request
from httptoolkit.response import AsyncStreamResponse, BaseResponse, Response
from httptoolkit.http_method import HttpMethod
from httptoolkit.sent_request import SentRequest
from httptoolkit.transport import BaseAsyncTransport


class AsyncService:
    def __init__(
        self,
        transport: BaseAsyncTransport,
        headers: Tuple[Header, ...] = (),
    ) -> None:
        self._transport = transport
        self._headers: Tuple[Header, ...] = headers

    @property
    def headers(self) -> Tuple[Header, ...]:
        return self._headers

    async def request(
        self,
        request: Request,
    ) -> Response:
        with self._managed_transport() as async_transport:
            sent_request, response = await async_transport.send(request)
            await self._validate_response(sent_request, response)
            return response

    async def post(
        self,
        path: str,
        headers: Tuple[Header, ...] = (),
        params: Optional[dict] = None,
        body: Optional[str] = None,
        json: Optional[Union[dict, List]] = None,
        files: Optional[Dict[str, Union[BinaryIO, Tuple[str, BinaryIO, str]]]] = None,
    ) -> Response:
        request = Request(
            method=HttpMethod.POST,
            path=path,
            headers=self.headers + headers,
            params=params,
            body=body,
            json=json,
            files=files,
        )
        return await self.request(request)

    async def patch(
        self,
        path: str,
        headers: Tuple[Header, ...] = (),
        params: Optional[dict] = None,
        body: Optional[str] = None,
        json: Optional[Union[dict, List]] = None,
        files: Optional[Dict[str, Union[BinaryIO, Tuple[str, BinaryIO, str]]]] = None,
    ) -> Response:
        request = Request(
            method=HttpMethod.PATCH,
            path=path,
            headers=self.headers + headers,
            params=params,
            body=body,
            json=json,
            files=files,
        )
        return await self.request(request)

    async def put(
        self,
        path: str,
        headers: Tuple[Header, ...] = (),
        params: Optional[dict] = None,
        body: Optional[str] = None,
        json: Optional[Union[dict, List]] = None,
        files: Optional[Dict[str, Union[BinaryIO, Tuple[str, BinaryIO, str]]]] = None,
    ) -> Response:
        request = Request(
            method=HttpMethod.PUT,
            path=path,
            headers=self.headers + headers,
            params=params,
            body=body,
            json=json,
            files=files,
        )
        return await self.request(request)

    async def delete(
        self,
        path: str,
        headers: Tuple[Header, ...] = (),
        params: Optional[dict] = None,
        body: Optional[str] = None,
        json: Optional[Union[dict, List]] = None,
        files: Optional[Dict[str, Union[BinaryIO, Tuple[str, BinaryIO, str]]]] = None,
    ) -> Response:
        request = Request(
            method=HttpMethod.DELETE,
            path=path,
            headers=self.headers + headers,
            params=params,
            body=body,
            json=json,
            files=files,
        )
        return await self.request(request)

    async def get(
        self,
        path: str,
        headers: Tuple[Header, ...] = (),
        params: Optional[dict] = None,
    ) -> Response:
        request = Request(
            method=HttpMethod.GET,
            path=path,
            headers=self.headers + headers,
            params=params,
            body=None,
            json=None,
            files=None,
        )
        return await self.request(request)

    @staticmethod
    async def _validate_response(sent_request: SentRequest, response: BaseResponse) -> None:
        if not response.ok:
            if isinstance(response, AsyncStreamResponse):
                await response.read()
            raise HttpError(sent_request, response)

    @asynccontextmanager
    async def stream_request(
        self,
        request: Request,
    ) -> AsyncIterator[AsyncStreamResponse]:
        with self._managed_transport() as transport:
            async with transport.stream(request) as (sent_request, async_stream_response):
                await self._validate_response(sent_request, async_stream_response)
                yield async_stream_response

    @asynccontextmanager
    async def post_stream(
        self,
        path: str,
        headers: Tuple[Header, ...] = (),
        params: Optional[dict] = None,
        body: Optional[str] = None,
        json: Optional[Union[dict, List]] = None,
        files: Optional[Dict[str, Union[BinaryIO, Tuple[str, BinaryIO, str]]]] = None,
    ) -> AsyncIterator[AsyncStreamResponse]:
        request = Request(
            method=HttpMethod.POST,
            path=path,
            headers=self.headers + headers,
            params=params,
            body=body,
            json=json,
            files=files,
        )
        async with self.stream_request(request) as async_stream_response:
            yield async_stream_response

    @asynccontextmanager
    async def patch_stream(
        self,
        path: str,
        headers: Tuple[Header, ...] = (),
        params: Optional[dict] = None,
        body: Optional[str] = None,
        json: Optional[Union[dict, List]] = None,
        files: Optional[Dict[str, Union[BinaryIO, Tuple[str, BinaryIO, str]]]] = None,
    ) -> AsyncIterator[AsyncStreamResponse]:
        request = Request(
            method=HttpMethod.PATCH,
            path=path,
            headers=self.headers + headers,
            params=params,
            body=body,
            json=json,
            files=files,
        )
        async with self.stream_request(request) as async_stream_response:
            yield async_stream_response

    @asynccontextmanager
    async def put_stream(
        self,
        path: str,
        headers: Tuple[Header, ...] = (),
        params: Optional[dict] = None,
        body: Optional[str] = None,
        json: Optional[Union[dict, List]] = None,
        files: Optional[Dict[str, Union[BinaryIO, Tuple[str, BinaryIO, str]]]] = None,
    ) -> AsyncIterator[AsyncStreamResponse]:
        request = Request(
            method=HttpMethod.PUT,
            path=path,
            headers=self.headers + headers,
            params=params,
            body=body,
            json=json,
            files=files,
        )
        async with self.stream_request(request) as async_stream_response:
            yield async_stream_response

    @asynccontextmanager
    async def delete_stream(
        self,
        path: str,
        headers: Tuple[Header, ...] = (),
        params: Optional[dict] = None,
        body: Optional[str] = None,
        json: Optional[Union[dict, List]] = None,
        files: Optional[Dict[str, Union[BinaryIO, Tuple[str, BinaryIO, str]]]] = None,
    ) -> AsyncIterator[AsyncStreamResponse]:
        request = Request(
            method=HttpMethod.DELETE,
            path=path,
            headers=self.headers + headers,
            params=params,
            body=body,
            json=json,
            files=files,
        )
        async with self.stream_request(request) as async_stream_response:
            yield async_stream_response

    @asynccontextmanager
    async def get_stream(
        self,
        path: str,
        headers: Tuple[Header, ...] = (),
        params: Optional[dict] = None,
    ) -> AsyncIterator[AsyncStreamResponse]:
        request = Request(
            method=HttpMethod.GET,
            path=path,
            headers=self.headers + headers,
            params=params,
            body=None,
            json=None,
            files=None,
        )
        async with self.stream_request(request) as async_stream_response:
            yield async_stream_response

    @contextmanager
    def _managed_transport(self) -> Iterator[BaseAsyncTransport]:
        try:
            yield self._transport

        except TransportError as exc:
            raise ServiceError(exc.request) from exc
