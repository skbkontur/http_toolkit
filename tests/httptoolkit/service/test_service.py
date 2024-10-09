import json
from datetime import timedelta

import httpx
import pytest
from pytest_httpx import HTTPXMock
from typing import Any

from httptoolkit import Header, HttpxService
from httptoolkit.errors import HttpError, ServiceError
from httptoolkit.service import Service
from httptoolkit.transport import HttpxTransport
from tests.httptoolkit.conftest import CustomJSONEncoder


@pytest.fixture
def service_with_only_url() -> HttpxService:
    return HttpxService(
        url="https://example.com:4321",
    )


@pytest.fixture
def service_with_custom_json_encoder() -> Service:
    return Service(
        transport=HttpxTransport(
            base_url="https://example.com:4321",
            json_encoder=lambda content: json.dumps(content, cls=CustomJSONEncoder),
        ),
    )


@pytest.mark.parametrize("method", ("get", "post", "put", "delete", "patch"))
def test_stream_requests_when_successful(
    method: str,
    service: Service,
    httpx_mock: HTTPXMock,
):
    response_text = "Schwarzenegger is a woman!"
    path = "/some/path"

    httpx_mock.add_response(
        method=method.upper(),
        url="https://example.com:4321" + path,
        text=response_text,
    )

    service_method = getattr(service, f"{method}_stream")

    with service_method(
        path, headers=(Header(name="RequestHeader", value="request-header", is_sensitive=False),)
    ) as stream_response:
        assert stream_response.status_code == 200
        assert response_text == stream_response.read().decode("utf8")

    calls = httpx_mock.get_requests()

    assert calls[0].headers["RequestHeader"] == "request-header"
    assert calls[0].headers["ServiceHeader"] == "service-header"


def test_post_when_response_is_successful(service, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url="https://example.com:4321/foo?foo=bar",
        text="Schwarzenegger is a woman!",
    )

    response = service.post(
        "/foo",
        headers=(Header(name="RequestHeader", value="request-header", is_sensitive=False),),
        params={"foo": "bar"},
        body="body",
    )

    assert response.text == "Schwarzenegger is a woman!"
    assert response.elapsed > timedelta(0)

    calls = httpx_mock.get_requests()

    assert calls[0].headers["ServiceHeader"] == "service-header"
    assert calls[0].headers["RequestHeader"] == "request-header"
    assert calls[0].content == b"body"


def test_post_when_response_is_not_successful(service, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url="https://example.com:4321/foo?foo=bar",
        text="Authorize first",
        status_code=401,
    )

    with pytest.raises(HttpError) as error:
        service.post(
            "/foo",
            headers=(Header(name="RequestHeader", value="request-header", is_sensitive=False),),
            params={"foo": "bar"},
            body="body",
        )

    assert "Authorize first" in str(error.value)
    assert error.value.response_code() == 401

    calls = httpx_mock.get_requests()

    assert calls[0].headers["ServiceHeader"] == "service-header"
    assert calls[0].headers["RequestHeader"] == "request-header"
    assert calls[0].content == b"body"


def test_post_when_transport_error(service, httpx_mock: HTTPXMock):
    httpx_mock.add_exception(
        method="POST",
        url="https://example.com:4321/foo?foo=bar",
        exception=httpx.TimeoutException("Timeout reached"),
    )

    with pytest.raises(ServiceError) as error:
        service.post(
            "/foo",
            headers=(Header(name="RequestHeader", value="request-header", is_sensitive=False),),
            params={"foo": "bar"},
            body="body",
        )

    assert "TimeoutException: Timeout reached" in str(error.value)

    calls = httpx_mock.get_requests()

    assert calls[0].headers["ServiceHeader"] == "service-header"
    assert calls[0].headers["RequestHeader"] == "request-header"
    assert calls[0].content == b"body"


def test_patch_when_response_is_successful(service, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="PATCH",
        url="https://example.com:4321/foo?foo=bar",
        text="Schwarzenegger is a woman!",
    )

    response = service.patch(
        "/foo",
        headers=(Header(name="RequestHeader", value="request-header", is_sensitive=False),),
        params={"foo": "bar"},
        body="body",
    )

    assert response.text == "Schwarzenegger is a woman!"
    assert response.elapsed > timedelta(0)

    calls = httpx_mock.get_requests()

    assert calls[0].headers["ServiceHeader"] == "service-header"
    assert calls[0].headers["RequestHeader"] == "request-header"
    assert calls[0].content == b"body"


def test_patch_when_response_is_not_successful(service, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="PATCH",
        url="https://example.com:4321/foo?foo=bar",
        text="Authorize first",
        status_code=401,
    )

    with pytest.raises(HttpError) as error:
        service.patch(
            "/foo",
            headers=(Header(name="RequestHeader", value="request-header", is_sensitive=False),),
            params={"foo": "bar"},
            body="body",
        )

    assert "Authorize first" in str(error.value)
    assert error.value.response_code() == 401

    calls = httpx_mock.get_requests()

    assert calls[0].headers["ServiceHeader"] == "service-header"
    assert calls[0].headers["RequestHeader"] == "request-header"
    assert calls[0].content == b"body"


def test_patch_when_transport_error(service, httpx_mock: HTTPXMock):
    httpx_mock.add_exception(
        method="PATCH",
        url="https://example.com:4321/foo?foo=bar",
        exception=httpx.TimeoutException("Timeout reached"),
    )

    with pytest.raises(ServiceError) as error:
        service.patch(
            "/foo",
            headers=(Header(name="RequestHeader", value="request-header", is_sensitive=False),),
            params={"foo": "bar"},
            body="body",
        )

    assert "TimeoutException: Timeout reached" in str(error.value)

    calls = httpx_mock.get_requests()

    assert calls[0].headers["ServiceHeader"] == "service-header"
    assert calls[0].headers["RequestHeader"] == "request-header"
    assert calls[0].content == b"body"


def test_get_when_response_is_successful(service, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url="https://example.com:4321/foo?foo=bar",
        text="Schwarzenegger is a woman!",
    )

    response = service.get(
        "/foo",
        headers=(Header(name="RequestHeader", value="request-header", is_sensitive=False),),
        params={"foo": "bar"},
    )

    assert response.text == "Schwarzenegger is a woman!"
    assert response.elapsed > timedelta(0)

    calls = httpx_mock.get_requests()

    assert calls[0].headers["ServiceHeader"] == "service-header"
    assert calls[0].headers["RequestHeader"] == "request-header"


def test_get_with_headers_tuple_when_response_is_successful(service, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url="https://example.com:4321/foo?foo=bar",
        text="Schwarzenegger is a woman!",
    )

    response = service.get(
        "/foo",
        headers=(Header(name="RequestHeader", value="request-header", is_sensitive=False),),
        params={"foo": "bar"},
    )

    assert response.text == "Schwarzenegger is a woman!"
    assert response.elapsed > timedelta(0)

    calls = httpx_mock.get_requests()

    assert calls[0].headers["ServiceHeader"] == "service-header"
    assert calls[0].headers["RequestHeader"] == "request-header"


def test_get_when_response_is_not_successful(service, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url="https://example.com:4321/foo",
        text="Authorize first",
        status_code=401,
    )

    with pytest.raises(HttpError) as error:
        service.get("/foo")

    assert "Authorize first" in str(error.value)
    assert error.value.response_code() == 401

    calls = httpx_mock.get_requests()

    assert calls[0].headers["ServiceHeader"] == "service-header"


def test_get_when_transport_error(service, httpx_mock: HTTPXMock):
    httpx_mock.add_exception(
        method="GET",
        url="https://example.com:4321/foo",
        exception=httpx.TimeoutException("Timeout reached"),
    )

    with pytest.raises(ServiceError) as error:
        service.get("/foo")

    assert "TimeoutException: Timeout reached" in str(error.value)

    calls = httpx_mock.get_requests()

    assert calls[0].headers["ServiceHeader"] == "service-header"


def test_put(service, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="PUT",
        url="https://example.com:4321/foo?foo=bar",
        text="Schwarzenegger is a woman!",
    )

    response = service.put(
        "/foo",
        headers=(Header(name="RequestHeader", value="request-header", is_sensitive=False),),
        params={"foo": "bar"},
        body="body",
    )

    assert response.text == "Schwarzenegger is a woman!"
    assert response.elapsed > timedelta(0)

    calls = httpx_mock.get_requests()

    assert calls[0].headers["ServiceHeader"] == "service-header"
    assert calls[0].headers["RequestHeader"] == "request-header"
    assert calls[0].content == b"body"


def test_delete(service, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="DELETE",
        url="https://example.com:4321/foo?foo=bar",
        text="Schwarzenegger is a woman!",
    )

    response = service.delete(
        "/foo",
        headers=(Header(name="RequestHeader", value="request-header", is_sensitive=False),),
        params={"foo": "bar"},
        body="body",
    )

    assert response.text == "Schwarzenegger is a woman!"
    assert response.elapsed > timedelta(0)

    calls = httpx_mock.get_requests()

    assert calls[0].headers["ServiceHeader"] == "service-header"
    assert calls[0].headers["RequestHeader"] == "request-header"
    assert calls[0].content == b"body"


def test_headers(service_with_only_url):
    assert service_with_only_url.headers == tuple()


@pytest.mark.parametrize("method", ("post", "put", "delete", "patch"))
def test_json_request_with_falsy_values(
    service: Service,
    httpx_mock: HTTPXMock,
    method: str,
) -> None:
    httpx_mock.add_response(
        method=method.upper(),
        url="https://example.com:4321/",
        text="OK",
    )

    falsy_values: Any = ({}, [], (), 0, 0.0, "", False)

    for json_value in falsy_values:
        response = getattr(service, method)(path="/", json=json_value)
        assert response.status_code == 200
        assert response.text == "OK"

    for request in httpx_mock.get_requests():
        assert request.headers["Content-Type"] == "application/json"


@pytest.mark.parametrize("method", ("post", "put", "delete", "patch"))
def test_json_request_with_none_value(
    service: Service,
    httpx_mock: HTTPXMock,
    method: str,
) -> None:
    httpx_mock.add_response(
        method=method.upper(),
        url="https://example.com:4321/",
        text="OK",
    )

    response = getattr(service, method)(path="/", json=None)

    assert response.status_code == 200
    assert response.text == "OK"
    assert response.elapsed > timedelta(0)

    request = httpx_mock.get_request()

    assert "Content-Type" not in request.headers
