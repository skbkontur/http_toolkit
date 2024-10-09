import json
from datetime import timedelta

import httpx
import pytest
from pytest_httpx import HTTPXMock
from typing import Any

from httptoolkit import Header, AsyncHttpxService
from httptoolkit.errors import HttpError, ServiceError
from httptoolkit.service import AsyncService
from httptoolkit.transport import AsyncHttpxTransport
from tests.httptoolkit.conftest import CustomJSONEncoder


class DummyAsyncService(AsyncService):
    pass


@pytest.fixture()
def async_service() -> AsyncService:
    return DummyAsyncService(
        transport=AsyncHttpxTransport(base_url="https://example.com", proxies={"http://": "http://10.10.1.10:3128"}),
        headers=(Header(name="ServiceHeader", value="async_service-header", is_sensitive=False),),
    )


@pytest.fixture
def async_service_with_custom_json_encoder() -> AsyncService:
    return AsyncService(
        transport=AsyncHttpxTransport(
            base_url="https://example.com:4321",
            json_encoder=lambda content: json.dumps(content, cls=CustomJSONEncoder),
        ),
    )


@pytest.fixture
def async_service_with_only_url() -> AsyncHttpxService:
    return AsyncHttpxService("https://example.com:4321")


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ("get", "post", "put", "delete", "patch"))
async def test_requests_when_successful(
    method: str,
    async_service: AsyncService,
    httpx_mock: HTTPXMock,
):
    response_text = "It's a boring text for test!"
    path = "/some/path"

    httpx_mock.add_response(
        method=method.upper(),
        url="https://example.com" + path,
        text=response_text,
    )

    service_method = getattr(async_service, method)

    response = await service_method(
        path,
        headers=(Header(name="RequestHeader", value="request-header", is_sensitive=False),),
    )

    assert response.status_code == 200
    assert response.text == response_text
    assert response.elapsed > timedelta(0)

    calls = httpx_mock.get_requests()

    assert calls[0].headers["RequestHeader"] == "request-header"
    assert calls[0].headers["ServiceHeader"] == "async_service-header"


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ("get", "post", "put", "delete", "patch"))
async def test_stream_requests_when_successful(
    method: str,
    async_service: AsyncService,
    httpx_mock: HTTPXMock,
):
    response_text = "It's a boring text for test!"
    path = "/some/path"

    httpx_mock.add_response(
        method=method.upper(),
        url="https://example.com" + path,
        text=response_text,
    )

    service_method = getattr(async_service, f"{method}_stream")

    async with service_method(
        path,
        headers=(Header(name="RequestHeader", value="request-header", is_sensitive=False),),
    ) as async_stream_response:
        assert async_stream_response.status_code == 200
        assert response_text == (await async_stream_response.read()).decode("utf8")

    calls = httpx_mock.get_requests()

    assert calls[0].headers["RequestHeader"] == "request-header"
    assert calls[0].headers["ServiceHeader"] == "async_service-header"


@pytest.mark.asyncio
async def test_post_when_request_successful(async_service: AsyncService, httpx_mock: HTTPXMock):
    response_text = "It's a boring text for test!"
    path = "/some/path"

    httpx_mock.add_response(
        method="POST",
        url="https://example.com" + path + "?foo=bar",
        text=response_text,
    )

    response = await async_service.post(
        path,
        headers=(Header(name="RequestHeader", value="request-header", is_sensitive=False),),
        params={"foo": "bar"},
        json={"param1": 1, "param2": 2},
    )

    assert response.status_code == 200
    assert response.elapsed > timedelta(0)
    assert response.text == response_text

    calls = httpx_mock.get_requests()

    assert calls[0].headers["RequestHeader"] == "request-header"
    assert calls[0].headers["ServiceHeader"] == "async_service-header"
    assert calls[0].headers["Content-Type"] == "application/json"
    assert calls[0].content == b'{"param1": 1, "param2": 2}'


@pytest.mark.asyncio
async def test_if_response_not_successful(async_service: AsyncService, httpx_mock: HTTPXMock):
    response_text = "Authorize first"
    path = "/some/path"

    httpx_mock.add_response(
        method="GET",
        url="https://example.com" + path + "?foo=bar",
        text=response_text,
        status_code=401,
    )

    with pytest.raises(HttpError) as error:
        await async_service.get(
            path,
            headers=(Header(name="RequestHeader", value="request-header", is_sensitive=False),),
            params={"foo": "bar"},
        )

    assert "Authorize first" in str(error.value)
    assert error.value.response_code() == 401

    calls = httpx_mock.get_requests()

    assert calls[0].headers["ServiceHeader"] == "async_service-header"
    assert calls[0].headers["RequestHeader"] == "request-header"


@pytest.mark.asyncio
async def test_post_when_transport_error(async_service: AsyncService, httpx_mock: HTTPXMock):
    path = "/some/path"

    httpx_mock.add_exception(
        method="POST",
        url="https://example.com" + path + "?foo=bar",
        exception=httpx.TimeoutException("Timeout reached"),
    )

    with pytest.raises(ServiceError) as error:
        await async_service.post(
            path,
            headers=(Header(name="RequestHeader", value="request-header", is_sensitive=False),),
            params={"foo": "bar"},
            body="body",
        )

    assert "TimeoutException: Timeout reached" in str(error.value)

    calls = httpx_mock.get_requests()

    assert calls[0].headers["ServiceHeader"] == "async_service-header"
    assert calls[0].headers["RequestHeader"] == "request-header"
    assert calls[0].content == b"body"


def test_headers(async_service_with_only_url):
    assert async_service_with_only_url.headers == ()


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ("post", "put", "delete", "patch"))
async def test_json_request_with_falsy_values(
    async_service: AsyncService,
    httpx_mock: HTTPXMock,
    method: str,
) -> None:
    httpx_mock.add_response(
        method=method.upper(),
        url="https://example.com/",
        text="OK",
    )

    falsy_values: Any = ({}, [], (), 0, 0.0, "", False)

    for json_value in falsy_values:
        response = await getattr(async_service, method)(path="/", json=json_value)
        assert response.status_code == 200
        assert response.elapsed > timedelta(0)
        assert response.text == "OK"

    for request in httpx_mock.get_requests():
        assert request.headers["Content-Type"] == "application/json"


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ("post", "put", "delete", "patch"))
async def test_json_request_with_none_value(
    async_service: AsyncService,
    httpx_mock: HTTPXMock,
    method: str,
) -> None:
    httpx_mock.add_response(
        method=method.upper(),
        url="https://example.com/",
        text="OK",
    )

    response = await getattr(async_service, method)(path="/", json=None)

    assert response.status_code == 200
    assert response.text == "OK"
    assert response.elapsed > timedelta(0)

    request = httpx_mock.get_request()

    assert "Content-Type" not in request.headers
