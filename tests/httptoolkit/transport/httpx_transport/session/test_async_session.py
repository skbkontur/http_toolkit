from datetime import timedelta
from typing import Iterable, Iterator, Type

import httpx
import pytest
from httpx import ConnectError, ConnectTimeout
from pytest_httpx import HTTPXMock

from httptoolkit.retry import RetryManager
from httptoolkit.transport._httpx._session._async import AsyncHttpxSession


def gen_responses(
    status_codes: Iterable[int],
    text: str,
    headers: dict,
) -> Iterator[httpx.Response]:
    for status_code in status_codes:
        yield httpx.Response(status_code=status_code, text=text, headers=headers)


@pytest.mark.asyncio
async def test_fail_then_success(httpx_mock: HTTPXMock):
    status_codes = tuple(RetryManager.DEFAULT_STATUS_CODES) + (200,)
    retry_max_attempts = len(status_codes)
    responses = gen_responses(status_codes, text="It's a boring text for test!", headers={"X-Custom-Header": "value"})

    httpx_mock.add_callback(
        method="GET",
        url="https://example.com:4321/foo?foo=bar",
        callback=lambda request: next(responses),
    )

    session = AsyncHttpxSession(
        retry_manager=RetryManager(
            max_attempts=retry_max_attempts,
            backoff_factor=0.01,
            exceptions=(ConnectError, ConnectTimeout),
            dont_retry_headers="Dont-Retry",
        )
    )
    response = await session.get("https://example.com:4321/foo", params={"foo": "bar"})

    assert response.text == "It's a boring text for test!"
    assert response.elapsed > timedelta(0)
    assert response.headers["X-Custom-Header"] == "value"

    calls = httpx_mock.get_requests()

    assert len(calls) == retry_max_attempts


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exc,exc_msg",
    [
        (httpx.ConnectTimeout, "Your time is over"),
        (httpx.ConnectError, "Smth goes wrong"),
    ],
)
async def test_retry_after_exception(
    httpx_mock: HTTPXMock,
    exc: Type[Exception],
    exc_msg: str,
):
    retry_max_attempts = 3

    httpx_mock.add_exception(
        method="GET",
        url="https://example.com:4321/foo?foo=bar",
        exception=exc(exc_msg),
    )

    session = AsyncHttpxSession(
        retry_manager=RetryManager(
            max_attempts=retry_max_attempts,
            backoff_factor=0.01,
            exceptions=(ConnectError, ConnectTimeout),
            dont_retry_headers="Dont-Retry",
        )
    )

    with pytest.raises(exc) as error:
        await session.get("https://example.com:4321/foo", params={"foo": "bar"})

    assert str(error.value) == exc_msg

    calls = httpx_mock.get_requests()

    assert len(calls) == retry_max_attempts


@pytest.mark.asyncio
async def test_retry_only_allowed_methods(httpx_mock: HTTPXMock):
    exc_msg = "Your time is over"

    httpx_mock.add_exception(
        method="GET",
        url="https://example.com:4321/foo?foo=bar",
        exception=httpx.ConnectTimeout(exc_msg),
    )

    session = AsyncHttpxSession(
        retry_manager=RetryManager(
            max_attempts=3,
            backoff_factor=0.01,
            methods=["POST"],
            exceptions=(ConnectError, ConnectTimeout),
            dont_retry_headers="Dont-Retry",
        )
    )

    with pytest.raises(httpx.ConnectTimeout) as error:
        await session.get("https://example.com:4321/foo", params={"foo": "bar"})

    assert str(error.value) == exc_msg

    calls = httpx_mock.get_requests()

    assert len(calls) == 1
