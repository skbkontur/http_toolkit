import json
import logging
import uuid
from datetime import timedelta
from json import JSONEncoder
from typing import BinaryIO, Type

import pytest
from pytest_httpx import HTTPXMock
from testfixtures import LogCapture

from httptoolkit import Header, HttpMethod
from httptoolkit.errors import TransportError
from httptoolkit.request import Request
from httptoolkit.transport import HttpxTransport

HTTPX_CLIENT_STATE_OPENED = 2


@pytest.fixture
def transport() -> HttpxTransport:
    return HttpxTransport(
        base_url="https://example.com:4321",
        allow_unverified_peer=False,
        open_timeout_in_seconds=1,
        read_timeout_in_seconds=1,
        retry_max_attempts=1,
        retry_backoff_factor=0,
        allow_post_retry=False,
        proxies={"http://": "http://10.10.1.10:3128"},
    )


@pytest.fixture
def transport_with_custom_encoder(custom_json_encoder: Type[JSONEncoder]) -> HttpxTransport:
    return HttpxTransport(
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


@pytest.fixture
def transport_with_custom_retry_status_codes(custom_json_encoder: Type[JSONEncoder]) -> HttpxTransport:
    return HttpxTransport(
        base_url="https://example.com:4321",
        allow_unverified_peer=False,
        open_timeout_in_seconds=1,
        read_timeout_in_seconds=1,
        retry_max_attempts=5,
        retry_backoff_factor=0.1,
        allow_post_retry=False,
        proxies={"http://": "http://10.10.1.10:3128"},
        retry_status_codes=[404],
    )


@pytest.fixture
def transport_with_empty_retry_status_codes(custom_json_encoder: Type[JSONEncoder]) -> HttpxTransport:
    return HttpxTransport(
        base_url="https://example.com:4321",
        allow_unverified_peer=False,
        open_timeout_in_seconds=1,
        read_timeout_in_seconds=1,
        retry_max_attempts=5,
        retry_backoff_factor=0.1,
        allow_post_retry=False,
        proxies={"http://": "http://10.10.1.10:3128"},
        retry_status_codes=[],
    )


@pytest.fixture
def transport_with_default_retry_status_codes(custom_json_encoder: Type[JSONEncoder]) -> HttpxTransport:
    return HttpxTransport(
        base_url="https://example.com:4321",
        allow_unverified_peer=False,
        open_timeout_in_seconds=1,
        read_timeout_in_seconds=1,
        retry_max_attempts=5,
        retry_backoff_factor=0.1,
        allow_post_retry=False,
        proxies={"http://": "http://10.10.1.10:3128"},
    )


def test_send_get_request(
    get_request,
    transport: HttpxTransport,
    httpx_mock: HTTPXMock,
) -> None:
    httpx_mock.add_response(
        method="GET",
        url="https://example.com:4321/put/some/data/here?please=True&carefully=True",
        text="It's a boring text for test!",
    )

    returned_request, response = transport.send(get_request)

    assert response.text == "It's a boring text for test!"
    assert response.elapsed > timedelta(0)

    calls = httpx_mock.get_requests()

    assert calls[0].headers["ServiceHeader"] == "service-header"
    assert calls[0].headers["RequestHeader"] == "request-header"
    assert calls[0].content == b""
    assert calls[0].extensions["timeout"] == {"connect": 1, "pool": None, "read": 1, "write": None}


def test_send_post_request(
    post_request,
    transport: HttpxTransport,
    httpx_mock: HTTPXMock,
) -> None:
    httpx_mock.add_response(
        method="POST",
        url="https://example.com:4321/put/some/data/here?please=True&carefully=True",
        text="It's a boring text for test!",
    )

    returned_request, response = transport.send(post_request)

    assert response.text == "It's a boring text for test!"
    assert response.elapsed > timedelta(0)

    calls = httpx_mock.get_requests()

    assert calls[0].headers["ServiceHeader"] == "service-header"
    assert calls[0].headers["RequestHeader"] == "request-header"
    assert calls[0].content == b"It always seems impossible until it's done."
    assert calls[0].extensions["timeout"] == {"connect": 1, "pool": None, "read": 1, "write": None}


def test_send_post_request_dict_json(
    x_request_dict_json,
    transport: HttpxTransport,
    httpx_mock: HTTPXMock,
) -> None:
    method, x_request = x_request_dict_json
    httpx_mock.add_response(
        method=method,
        url="https://example.com:4321/put/some/data/here?please=True&carefully=True",
        text="It's a boring text for test!",
    )

    returned_request, response = transport.send(x_request)

    assert response.text == "It's a boring text for test!"
    assert response.elapsed > timedelta(0)

    calls = httpx_mock.get_requests()

    assert calls[0].headers["ServiceHeader"] == "service-header"
    assert calls[0].headers["RequestHeader"] == "request-header"
    assert calls[0].headers["Content-Type"] == "application/json"
    assert calls[0].headers["Content-Length"] == "26"
    assert calls[0].content == b'{"param1": 1, "param2": 2}'
    assert calls[0].extensions["timeout"] == {"connect": 1, "pool": None, "read": 1, "write": None}


def test_send_post_request_list_json(
    x_request_list_json,
    transport: HttpxTransport,
    httpx_mock: HTTPXMock,
) -> None:
    method, x_request = x_request_list_json
    httpx_mock.add_response(
        method=method,
        url="https://example.com:4321/put/some/data/here?please=True&carefully=True",
        text="It's a boring text for test!",
    )

    returned_request, response = transport.send(x_request)

    assert response.text == "It's a boring text for test!"
    assert response.elapsed > timedelta(0)

    calls = httpx_mock.get_requests()

    assert calls[0].headers["ServiceHeader"] == "service-header"
    assert calls[0].headers["RequestHeader"] == "request-header"
    assert calls[0].headers["Content-Type"] == "application/json"
    assert calls[0].headers["Content-Length"] == "56"
    assert calls[0].content == b'[{"param1": 1, "param2": 2}, {"param3": 3, "param4": 4}]'
    assert calls[0].extensions["timeout"] == {"connect": 1, "pool": None, "read": 1, "write": None}


def test_send_post_request_custom_json(
    x_custom_request_json,
    transport_with_custom_encoder: HttpxTransport,
    httpx_mock: HTTPXMock,
) -> None:
    method, x_request = x_custom_request_json
    httpx_mock.add_response(
        method=method,
        url="https://example.com:4321/put/some/data/here?please=True&carefully=True",
        text="It's a boring text for test!",
    )
    returned_request, response = transport_with_custom_encoder.send(x_request)

    assert response.text == "It's a boring text for test!"
    assert response.elapsed > timedelta(0)

    calls = httpx_mock.get_requests()

    assert calls[0].headers["ServiceHeader"] == "service-header"
    assert calls[0].headers["RequestHeader"] == "request-header"
    assert calls[0].headers["Content-Type"] == "application/json"
    assert calls[0].headers["Content-Length"] == "69"
    assert calls[0].content == b'{"param1": 1, "param2": 2, "time": "07/17/2023", "decimal": "0.5656"}'
    assert calls[0].extensions["timeout"] == {"connect": 1, "pool": None, "read": 1, "write": None}


def test_send_post_request_file(
    x_request_file,
    transport: HttpxTransport,
    httpx_mock: HTTPXMock,
) -> None:
    method, x_request = x_request_file
    httpx_mock.add_response(
        method=method,
        url="https://example.com:4321/put/some/data/here?please=True&carefully=True",
        text="It's a boring text for test!",
    )

    returned_request, response = transport.send(x_request)

    assert response.text == "It's a boring text for test!"
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


def test_send_post_request_file_without_content_type(
    transport: HttpxTransport, httpx_mock: HTTPXMock, test_file: BinaryIO
) -> None:
    request = Request(HttpMethod.POST, "/", {}, files={"upload-file": test_file})
    httpx_mock.add_response(method="POST")
    transport.send(request)

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


def test_send_post_request_forms(transport: HttpxTransport, httpx_mock: HTTPXMock, test_file: BinaryIO) -> None:
    request = Request(HttpMethod.POST, "/", {}, files={"upload-file": ("test.csv", test_file, "text/csv")})
    httpx_mock.add_response(method="POST")
    transport.send(request)

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


def test_send_post_request_error_json_and_files(
    transport: HttpxTransport, httpx_mock: HTTPXMock, test_file: BinaryIO
) -> None:
    request = Request(HttpMethod.POST, "/", {}, files={"upload-file": test_file}, json={"param1": 1, "param2": 2})
    with pytest.raises(RuntimeError) as error:
        transport.send(request)
    assert str(error.value) == "json and files can't be sent together"


def test_send_post_request_error_json_and_body(
    transport: HttpxTransport, httpx_mock: HTTPXMock, test_file: BinaryIO
) -> None:
    request = Request(
        HttpMethod.POST, "/", {}, body="Just another boring text for test!", json={"param1": 1, "param2": 2}
    )
    with pytest.raises(RuntimeError) as error:
        transport.send(request)
    assert str(error.value) == "json and body can't be sent together"


def test_sends_serialized_uuid(
    transport: HttpxTransport,
    httpx_mock: HTTPXMock,
) -> None:
    request = Request(
        method=HttpMethod.POST,
        path="/put/some/data/here",
        json={"user_id": uuid.UUID("9d1e286b-3ee0-4fb5-813e-6125f5b5d1b5")},
        params={},
        headers=(Header(name="ServiceHeader", value="service-header", is_sensitive=False),),
    )

    httpx_mock.add_response(
        method="POST",
        url="https://example.com:4321/put/some/data/here",
    )

    transport.send(request)

    httpx_request = httpx_mock.get_request()
    assert httpx_request.headers["Content-Type"] == "application/json"
    assert httpx_request.content == b'{"user_id": "9d1e286b-3ee0-4fb5-813e-6125f5b5d1b5"}'
    assert httpx_request.extensions["timeout"] == {"connect": 1, "pool": None, "read": 1, "write": None}


def test_send_patch_request(
    patch_request,
    transport: HttpxTransport,
    httpx_mock: HTTPXMock,
) -> None:
    httpx_mock.add_response(
        method="PATCH",
        url="https://example.com:4321/put/some/data/here?please=True&carefully=True",
        text="It's a boring text for test!",
    )

    returned_request, response = transport.send(patch_request)

    assert response.text == "It's a boring text for test!"
    assert response.elapsed > timedelta(0)

    calls = httpx_mock.get_requests()

    assert calls[0].headers["ServiceHeader"] == "service-header"
    assert calls[0].headers["RequestHeader"] == "request-header"
    assert calls[0].content == b"It always seems impossible until it's done."
    assert calls[0].extensions["timeout"] == {"connect": 1, "pool": None, "read": 1, "write": None}


def test_request_when_error_occurs(
    get_request,
    transport: HttpxTransport,
    httpx_mock: HTTPXMock,
) -> None:
    httpx_mock.add_exception(
        method="GET",
        url="https://example.com:4321/put/some/data/here?please=True&carefully=True",
        exception=Exception("Unexpected!"),
    )

    with pytest.raises(TransportError) as error:
        transport.send(get_request)

    assert str(error.value) == "Exception: Unexpected!"


def test_logging_request(
    post_request,
    transport: HttpxTransport,
    httpx_mock: HTTPXMock,
) -> None:
    httpx_mock.add_response(
        method="POST",
        url="https://example.com:4321/put/some/data/here?please=True&carefully=True",
        text="It's a boring text for test!",
    )

    with LogCapture(level=logging.INFO) as capture:
        transport.send(post_request)

    capture.check(
        (
            "httptoolkit.transport._httpx._sync",
            "INFO",
            "Sending POST https://example.com:4321/put/some/data/here?please=True&carefully=True (body: 46)",
        )
    )


def test_session_is_not_closed_after_response(
    get_request,
    transport: HttpxTransport,
    httpx_mock: HTTPXMock,
) -> None:
    httpx_mock.add_response(
        method="GET",
        url="https://example.com:4321/put/some/data/here?please=True&carefully=True",
        text="It's a boring text for test!",
    )

    transport.send(get_request)

    assert transport._session._state.value == HTTPX_CLIENT_STATE_OPENED


def test_session_is_not_closed_after_error(
    get_request,
    transport: HttpxTransport,
    httpx_mock: HTTPXMock,
) -> None:
    httpx_mock.add_exception(
        method="GET",
        url="https://example.com:4321/put/some/data/here?please=True&carefully=True",
        exception=Exception("Something went wrong"),
    )

    with pytest.raises(Exception) as exception_info:
        transport.send(get_request)

    assert str(exception_info.value) == "Exception: Something went wrong"
    assert transport._session._state.value == HTTPX_CLIENT_STATE_OPENED


def test_allow_post_retry(transport) -> None:
    transport_allow_post_retry = HttpxTransport(
        base_url="",
        allow_unverified_peer=False,
        open_timeout_in_seconds=1,
        read_timeout_in_seconds=1,
        retry_max_attempts=1,
        retry_backoff_factor=0,
        allow_post_retry=True,
        proxies={},
    )

    assert "POST" not in transport._session._retry_manager._methods

    assert "POST" in transport_allow_post_retry._session._retry_manager._methods


def test_returned_request(
    transport,
    httpx_mock: HTTPXMock,
) -> None:
    httpx_mock.add_response()

    request = Request(
        method=HttpMethod.GET,
        path="",
        headers=(
            Header(name="Sensitive", value="Sensitive", is_sensitive=True),
            Header(name="CamelCase", value="CamelCase", is_sensitive=False),
            Header(name="Kebab-Case", value="Kebab-Case", is_sensitive=False),
            Header(name="Snake_Case", value="Snake_Case", is_sensitive=False),
        ),
        params={},
        body="Content",
    )
    returned_request, _ = transport.send(request)

    assert sorted(returned_request.headers, key=lambda i: i.name) == [
        Header(name="accept", value="*/*", is_sensitive=False),
        Header(name="accept-encoding", value="gzip, deflate", is_sensitive=False),
        Header(name="camelcase", value="CamelCase", is_sensitive=False),
        Header(name="connection", value="keep-alive", is_sensitive=False),
        Header(name="content-length", value="7", is_sensitive=False),
        Header(name="host", value="example.com:4321", is_sensitive=False),
        Header(name="kebab-case", value="Kebab-Case", is_sensitive=False),
        Header(name="sensitive", value="Sensitive", is_sensitive=True),
        Header(name="snake_case", value="Snake_Case", is_sensitive=False),
        Header(name="user-agent", value="python-httpx/0.24.1", is_sensitive=False),
    ]
    assert returned_request.url == "https://example.com:4321/"
    assert returned_request.method == "GET"
    assert returned_request.body == b"Content"
    assert returned_request.proxies == {"http://": "http://10.10.1.10:3128"}


def test_custom_retry_status_codes(
    get_request, httpx_mock: HTTPXMock, transport_with_custom_retry_status_codes: HttpxTransport
) -> None:
    httpx_mock.add_response(method="GET", url="https://example.com:4321/put/some/data/here", status_code=404)
    httpx_mock.add_response(method="GET", url="https://example.com:4321/put/some/data/here", status_code=200)

    request = Request(method=HttpMethod.GET, path="/put/some/data/here", params={})

    sent_request, response = transport_with_custom_retry_status_codes.send(request)

    assert response.status_code == 200


def test_empty_retry_status_codes(
    get_request, httpx_mock: HTTPXMock, transport_with_empty_retry_status_codes: HttpxTransport
) -> None:
    httpx_mock.add_response(method="GET", url="https://example.com:4321/put/some/data/here", status_code=413)

    request = Request(method=HttpMethod.GET, path="/put/some/data/here", params={})
    sent_request, response = transport_with_empty_retry_status_codes.send(request)

    assert response.status_code == 413


def test_default_retry_status_codes(
    get_request, httpx_mock: HTTPXMock, transport_with_default_retry_status_codes: HttpxTransport
) -> None:
    httpx_mock.add_response(method="GET", url="https://example.com:4321/put/some/data/here", status_code=413)
    httpx_mock.add_response(method="GET", url="https://example.com:4321/put/some/data/here", status_code=200)

    request = Request(method=HttpMethod.GET, path="/put/some/data/here", params={})

    sent_request, response = transport_with_default_retry_status_codes.send(request)

    assert response.status_code == 200
