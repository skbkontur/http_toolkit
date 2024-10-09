import json
import logging
from datetime import timedelta
from json import JSONEncoder
from typing import BinaryIO, Type

import pytest
from pytest_httpx import HTTPXMock
from testfixtures import LogCapture

from httptoolkit import HttpMethod
from httptoolkit.errors import TransportError
from httptoolkit.request import Request
from httptoolkit.transport import AsyncHttpxTransport

HTTPX_CLIENT_STATE_OPENED = 2


@pytest.fixture
def async_transport() -> AsyncHttpxTransport:
    return AsyncHttpxTransport(
        base_url="https://example.com:4321",
        allow_unverified_peer=False,
        open_timeout_in_seconds=1,
        read_timeout_in_seconds=1,
        retry_max_attempts=1,
        retry_backoff_factor=0,
        allow_post_retry=False,
        proxies={},
    )


@pytest.fixture
def async_transport_with_custom_encoder(custom_json_encoder: Type[JSONEncoder]) -> AsyncHttpxTransport:
    return AsyncHttpxTransport(
        base_url="https://example.com:4321",
        allow_unverified_peer=False,
        open_timeout_in_seconds=1,
        read_timeout_in_seconds=1,
        retry_max_attempts=1,
        retry_backoff_factor=0,
        allow_post_retry=False,
        proxies={},
        json_encoder=lambda content: json.dumps(content, cls=custom_json_encoder),
    )


@pytest.mark.asyncio
async def test_send_get_request(
    get_request,
    async_transport: AsyncHttpxTransport,
    httpx_mock: HTTPXMock,
) -> None:
    httpx_mock.add_response(
        method="GET",
        url="https://example.com:4321/put/some/data/here?please=True&carefully=True",
        text="Schwarzenegger is a woman!",
    )

    returned_request, response = await async_transport.send(get_request)

    assert response.text == "Schwarzenegger is a woman!"
    assert response.elapsed > timedelta(0)

    calls = httpx_mock.get_requests()

    assert calls[0].headers["ServiceHeader"] == "service-header"
    assert calls[0].headers["RequestHeader"] == "request-header"
    assert calls[0].content == b""
    assert calls[0].extensions["timeout"] == {"connect": 1, "pool": None, "read": 1, "write": None}


@pytest.mark.asyncio
async def test_send_post_request(
    post_request,
    async_transport: AsyncHttpxTransport,
    httpx_mock: HTTPXMock,
) -> None:
    httpx_mock.add_response(
        method="POST",
        url="https://example.com:4321/put/some/data/here?please=True&carefully=True",
        text="Schwarzenegger is a woman!",
    )

    returned_request, response = await async_transport.send(post_request)

    assert response.text == "Schwarzenegger is a woman!"
    assert response.elapsed > timedelta(0)

    calls = httpx_mock.get_requests()

    assert calls[0].headers["ServiceHeader"] == "service-header"
    assert calls[0].headers["RequestHeader"] == "request-header"
    assert calls[0].content == b"It always seems impossible until it's done."
    assert calls[0].extensions["timeout"] == {"connect": 1, "pool": None, "read": 1, "write": None}


@pytest.mark.asyncio
async def test_send_post_request_json(
    x_request_dict_json,
    async_transport: AsyncHttpxTransport,
    httpx_mock: HTTPXMock,
) -> None:
    method, x_request = x_request_dict_json
    httpx_mock.add_response(
        method=method,
        url="https://example.com:4321/put/some/data/here?please=True&carefully=True",
        text="Schwarzenegger is a woman!",
    )

    returned_request, response = await async_transport.send(x_request)

    assert response.text == "Schwarzenegger is a woman!"
    assert response.elapsed > timedelta(0)

    calls = httpx_mock.get_requests()

    assert calls[0].headers["ServiceHeader"] == "service-header"
    assert calls[0].headers["RequestHeader"] == "request-header"
    assert calls[0].headers["Content-Type"] == "application/json"
    assert calls[0].content == b'{"param1": 1, "param2": 2}'
    assert calls[0].extensions["timeout"] == {"connect": 1, "pool": None, "read": 1, "write": None}


@pytest.mark.asyncio
async def test_send_post_request_list_json(
    x_request_list_json,
    async_transport: AsyncHttpxTransport,
    httpx_mock: HTTPXMock,
) -> None:
    method, x_request = x_request_list_json
    httpx_mock.add_response(
        method=method,
        url="https://example.com:4321/put/some/data/here?please=True&carefully=True",
        text="Schwarzenegger is a woman!",
    )

    returned_request, response = await async_transport.send(x_request)

    assert response.text == "Schwarzenegger is a woman!"
    assert response.elapsed > timedelta(0)

    calls = httpx_mock.get_requests()

    assert calls[0].headers["ServiceHeader"] == "service-header"
    assert calls[0].headers["RequestHeader"] == "request-header"
    assert calls[0].headers["Content-Type"] == "application/json"
    assert calls[0].content == b'[{"param1": 1, "param2": 2}, {"param3": 3, "param4": 4}]'
    assert calls[0].extensions["timeout"] == {"connect": 1, "pool": None, "read": 1, "write": None}


@pytest.mark.asyncio
async def test_send_post_request_custom_json(
    x_custom_request_json,
    async_transport_with_custom_encoder: AsyncHttpxTransport,
    httpx_mock: HTTPXMock,
) -> None:
    method, x_request = x_custom_request_json
    httpx_mock.add_response(
        method=method,
        url="https://example.com:4321/put/some/data/here?please=True&carefully=True",
        text="Schwarzenegger is a woman!",
    )

    returned_request, response = await async_transport_with_custom_encoder.send(x_request)

    assert response.text == "Schwarzenegger is a woman!"
    assert response.elapsed > timedelta(0)

    calls = httpx_mock.get_requests()

    assert calls[0].headers["RequestHeader"] == "request-header"
    assert calls[0].headers["Content-Type"] == "application/json"
    assert calls[0].content == b'{"param1": 1, "param2": 2, "time": "07/17/2023", "decimal": "0.5656"}'
    assert calls[0].extensions["timeout"] == {"connect": 1, "pool": None, "read": 1, "write": None}


@pytest.mark.asyncio
async def test_send_post_request_file(
    x_request_file,
    async_transport: AsyncHttpxTransport,
    httpx_mock: HTTPXMock,
) -> None:
    method, x_request = x_request_file
    httpx_mock.add_response(
        method=method,
        url="https://example.com:4321/put/some/data/here?please=True&carefully=True",
        text="Schwarzenegger is a woman!",
    )

    returned_request, response = await async_transport.send(x_request)

    assert response.text == "Schwarzenegger is a woman!"
    assert response.elapsed > timedelta(0)

    calls = httpx_mock.get_requests()

    assert calls[0].headers["RequestHeader"] == "request-header"
    assert calls[0].headers["Content-Type"] == "multipart/form-data; boundary=secretboundary"
    assert calls[0].headers["Content-Length"] == "235"
    assert calls[0].content == (
        b'--secretboundary\r\nContent-Disposition: form-data; name="data"\r\n\r\nSta'
        b"llone is a Woman\r\n--secretboundary\r\nContent-Disposition: form-data; name"
        b'="upload-file"; filename="test.csv"\r\nContent-Type: text/csv\r\n\r\nHi, w'
        b"orld!\r\n--secretboundary--\r\n"
    )
    assert calls[0].extensions["timeout"] == {"connect": 1, "pool": None, "read": 1, "write": None}


@pytest.mark.asyncio
async def test_send_post_request_file_without_content_type(
    async_transport: AsyncHttpxTransport, httpx_mock: HTTPXMock, test_file: BinaryIO
) -> None:
    request = Request(HttpMethod.POST, "/", {}, files={"upload-file": test_file})
    httpx_mock.add_response(method="POST")
    await async_transport.send(request)

    sent = httpx_mock.get_request()
    boundary = sent.headers["Content-Type"].split("boundary=")[-1]
    boundary_bytes = boundary.encode("ascii")

    assert sent.headers["Content-Type"] == f"multipart/form-data; boundary={boundary}"
    assert sent.headers["Content-Length"] == "185"
    assert sent.content == (
        b"--" + boundary_bytes + b"\r\n"
        b'Content-Disposition: form-data; name="upload-file"; filename="test.csv"\r\n'
        b"Content-Type: text/csv\r\n\r\n"
        b"Hi, world!\r\n"
        b"--" + boundary_bytes + b"--\r\n"
    )
    assert sent.extensions["timeout"] == {"connect": 1, "pool": None, "read": 1, "write": None}


@pytest.mark.asyncio
async def test_send_post_request_forms(
    async_transport: AsyncHttpxTransport, httpx_mock: HTTPXMock, test_file: BinaryIO
) -> None:
    request = Request(HttpMethod.POST, "/", {}, files={"upload-file": ("test.csv", test_file, "text/csv")})
    httpx_mock.add_response(method="POST")
    await async_transport.send(request)

    sent = httpx_mock.get_request()
    boundary = sent.headers["Content-Type"].split("boundary=")[-1]
    boundary_bytes = boundary.encode("ascii")

    assert sent.headers["Content-Type"] == f"multipart/form-data; boundary={boundary}"
    assert sent.headers["Content-Length"] == "185"
    assert sent.content == (
        b"--" + boundary_bytes + b"\r\n"
        b'Content-Disposition: form-data; name="upload-file"; filename="test.csv"\r\n'
        b"Content-Type: text/csv\r\n\r\n"
        b"Hi, world!\r\n"
        b"--" + boundary_bytes + b"--\r\n"
    )
    assert sent.extensions["timeout"] == {"connect": 1, "pool": None, "read": 1, "write": None}


@pytest.mark.asyncio
async def test_send_post_request_error_json_and_files(
    async_transport: AsyncHttpxTransport, httpx_mock: HTTPXMock, test_file: BinaryIO
) -> None:
    request = Request(HttpMethod.POST, "/", {}, files={"upload-file": test_file}, json={"param1": 1, "param2": 2})
    with pytest.raises(RuntimeError) as error:
        await async_transport.send(request)
    assert str(error.value) == "json and files can't be sent together"


@pytest.mark.asyncio
async def test_send_post_request_error_json_and_body(
    async_transport: AsyncHttpxTransport, httpx_mock: HTTPXMock, test_file: BinaryIO
) -> None:
    request = Request(HttpMethod.POST, "/", {}, body="Stallone is a Woman!", json={"param1": 1, "param2": 2})
    with pytest.raises(RuntimeError) as error:
        await async_transport.send(request)
    assert str(error.value) == "json and body can't be sent together"


@pytest.mark.asyncio
async def test_send_patch_request(
    patch_request,
    async_transport: AsyncHttpxTransport,
    httpx_mock: HTTPXMock,
) -> None:
    httpx_mock.add_response(
        method="PATCH",
        url="https://example.com:4321/put/some/data/here?please=True&carefully=True",
        text="Schwarzenegger is a woman!",
    )

    returned_request, response = await async_transport.send(patch_request)

    assert response.text == "Schwarzenegger is a woman!"
    assert response.elapsed > timedelta(0)

    calls = httpx_mock.get_requests()

    assert calls[0].headers["ServiceHeader"] == "service-header"
    assert calls[0].headers["RequestHeader"] == "request-header"
    assert calls[0].content == b"It always seems impossible until it's done."
    assert calls[0].extensions["timeout"] == {"connect": 1, "pool": None, "read": 1, "write": None}


@pytest.mark.asyncio
async def test_request_when_error_occurs(
    get_request,
    async_transport: AsyncHttpxTransport,
    httpx_mock: HTTPXMock,
) -> None:
    httpx_mock.add_exception(
        method="GET",
        url="https://example.com:4321/put/some/data/here?please=True&carefully=True",
        exception=Exception("Unexpected!"),
    )

    with pytest.raises(TransportError) as error:
        await async_transport.send(get_request)

    assert str(error.value) == "Exception: Unexpected!"


@pytest.mark.asyncio
async def test_logging_request(
    post_request,
    async_transport: AsyncHttpxTransport,
    httpx_mock: HTTPXMock,
) -> None:
    httpx_mock.add_response(
        method="POST",
        url="https://example.com:4321/put/some/data/here?please=True&carefully=True",
        text="Schwarzenegger is a woman!",
    )

    with LogCapture(level=logging.INFO) as capture:
        await async_transport.send(post_request)

    capture.check(
        (
            "httptoolkit.transport._httpx._async",
            "INFO",
            "Sending POST https://example.com:4321/put/some/data/here?please=True&carefully=True (body: 46)",
        )
    )


@pytest.mark.asyncio
async def test_session_is_not_closed_after_response(
    get_request,
    async_transport: AsyncHttpxTransport,
    httpx_mock: HTTPXMock,
) -> None:
    httpx_mock.add_response(
        method="GET",
        url="https://example.com:4321/put/some/data/here?please=True&carefully=True",
        text="Schwarzenegger is a woman!",
    )

    await async_transport.send(get_request)

    assert async_transport._session._state.value == HTTPX_CLIENT_STATE_OPENED


@pytest.mark.asyncio
async def test_session_is_not_closed_after_error(
    get_request,
    async_transport: AsyncHttpxTransport,
    httpx_mock: HTTPXMock,
) -> None:
    exception_message = "Something went wrong"
    httpx_mock.add_exception(
        method="GET",
        url="https://example.com:4321/put/some/data/here?please=True&carefully=True",
        exception=Exception(exception_message),
    )

    with pytest.raises(Exception) as exception_info:
        await async_transport.send(get_request)

    assert str(exception_info.value) == "Exception: Something went wrong"
    assert async_transport._session._state.value == HTTPX_CLIENT_STATE_OPENED


def test_allow_post_retry(async_transport) -> None:
    transport_allow_post_retry = AsyncHttpxTransport(
        base_url="",
        allow_unverified_peer=False,
        open_timeout_in_seconds=1,
        read_timeout_in_seconds=1,
        retry_max_attempts=1,
        retry_backoff_factor=0,
        allow_post_retry=True,
        proxies={},
    )

    assert "POST" not in async_transport._session._retry_manager._methods

    assert "POST" in transport_allow_post_retry._session._retry_manager._methods
