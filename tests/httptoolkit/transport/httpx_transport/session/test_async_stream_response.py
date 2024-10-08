import pytest
from httpx import ByteStream, Request as OriginalRequest, ConnectError, ConnectTimeout
from pytest_httpx import HTTPXMock

from httptoolkit.response import AsyncStreamResponse
from httptoolkit.retry import RetryManager
from httptoolkit.transport._httpx._session._async import AsyncHttpxSession


@pytest.fixture
def async_session():
    return AsyncHttpxSession(
        retry_manager=RetryManager(
            max_attempts=5,
            backoff_factor=0.01,
            exceptions=(ConnectError, ConnectTimeout),
            dont_retry_headers="Dont-Retry",
        )
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ("GET", "POST", "PUT", "DELETE", "PATCH"))
async def test_stream_response(
    method: str,
    async_session: AsyncHttpxSession,
    httpx_mock: HTTPXMock,
):
    response_text = "first line\nsecond line\n"
    url = "http://example.com/foo/bar"

    httpx_mock.add_response(
        method=method.upper(),
        url=url,
        stream=ByteStream(response_text.encode("utf8")),
    )

    async with async_session.stream(OriginalRequest(method, url)) as httpx_response:
        async_stream_response = AsyncStreamResponse(httpx_response)
        assert async_stream_response.status_code == 200
        assert [chunk async for chunk in async_stream_response.iter_text(7)] == [
            "first l",
            "ine\nsec",
            "ond lin",
            "e\n",
        ]

    async with async_session.stream(OriginalRequest(method, url)) as httpx_response:
        async_stream_response = AsyncStreamResponse(httpx_response)
        assert async_stream_response.status_code == 200
        assert [chunk async for chunk in async_stream_response.iter_bytes(7)] == [
            b"first l",
            b"ine\nsec",
            b"ond lin",
            b"e\n",
        ]

    async with async_session.stream(OriginalRequest(method, url)) as httpx_response:
        async_stream_response = AsyncStreamResponse(httpx_response)
        assert async_stream_response.status_code == 200
        assert [chunk async for chunk in async_stream_response.iter_lines()] == ["first line", "second line"]

    async with async_session.stream(OriginalRequest(method, url)) as httpx_response:
        async_stream_response = AsyncStreamResponse(httpx_response)
        assert async_stream_response.status_code == 200
        assert [chunk async for chunk in async_stream_response.iter_raw(7)] == [
            b"first l",
            b"ine\nsec",
            b"ond lin",
            b"e\n",
        ]

    async with async_session.stream(OriginalRequest(method, url)) as httpx_response:
        async_stream_response = AsyncStreamResponse(httpx_response)
        assert async_stream_response.status_code == 200
        assert (await async_stream_response.read()).decode("utf8") == response_text


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ("GET", "POST", "PUT", "DELETE", "PATCH"))
async def test_elapsed_not_available_until_async_response_closed(
    method: str,
    async_session: AsyncHttpxSession,
    httpx_mock: HTTPXMock,
):
    response_text = "first line\nsecond line\n"
    url = "http://example.com/foo/bar"

    httpx_mock.add_response(
        method=method.upper(),
        url=url,
        stream=ByteStream(response_text.encode("utf8")),
    )

    async with async_session.stream(OriginalRequest(method, url)) as httpx_response:
        async_stream_response = AsyncStreamResponse(httpx_response)
        assert async_stream_response.status_code == 200
        with pytest.raises(RuntimeError) as error:
            async_stream_response.elapsed
        assert str(error.value) == "'.elapsed' may only be accessed after the response has been read or closed."
