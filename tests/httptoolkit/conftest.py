import datetime
import decimal
import os
from datetime import date
from typing import TYPE_CHECKING, Any, Generic, TypeVar, Tuple, Type, BinaryIO, Set

import pytest
from _decimal import Decimal

from httptoolkit import Header
from httptoolkit.encoder import DefaultJSONEncoder
from httptoolkit.request import Request
from httptoolkit.service import Service
from httptoolkit.transport import HttpxTransport
from httptoolkit.sent_request import SentRequest
from httptoolkit import HttpMethod

if TYPE_CHECKING:
    from pytest import FixtureRequest as _FixtureRequest

    T = TypeVar("T")

    class FixtureRequest(_FixtureRequest, Generic[T]):
        param: T


class DummyService(Service):
    pass


class CustomJSONEncoder(DefaultJSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        if isinstance(obj, datetime.date):
            return obj.strftime("%m/%d/%Y")
        return super().default(obj)


@pytest.fixture
def get_request() -> Request:
    return Request(
        method=HttpMethod.GET,
        path="/put/some/data/here",
        headers=(
            Header(name="ServiceHeader", value="service-header", is_sensitive=False),
            Header(name="RequestHeader", value="request-header", is_sensitive=False),
        ),
        params={"please": True, "carefully": True},
        body=None,
    )


@pytest.fixture
def get_sent_request(get_request) -> SentRequest:
    return SentRequest(
        request=get_request,
        base_url="https://example.com:4321",
        headers=(
            Header(name="ServiceHeader", value="service-header", is_sensitive=False),
            Header(name="RequestHeader", value="request-header", is_sensitive=False),
        ),
        body=None,
        proxies={"http://": "http://10.10.1.10:3128"},
    )


@pytest.fixture
def post_request() -> Request:
    return Request(
        method=HttpMethod.POST,
        path="/put/some/data/here",
        headers=(
            Header(name="ServiceHeader", value="service-header", is_sensitive=False),
            Header(name="RequestHeader", value="request-header", is_sensitive=False),
        ),
        params={"please": True, "carefully": True},
        body="It always seems impossible until it's done.",
    )


@pytest.fixture
def post_sent_request(post_request) -> SentRequest:
    return SentRequest(
        request=post_request,
        base_url="https://example.com:4321",
        headers=(
            Header(name="ServiceHeader", value="service-header", is_sensitive=False),
            Header(name="RequestHeader", value="request-header", is_sensitive=False),
        ),
        body="It always seems impossible until it's done.",
        proxies={"http://": "http://10.10.1.10:3128"},
    )


@pytest.fixture(params=[HttpMethod.POST, HttpMethod.PATCH, HttpMethod.PUT, HttpMethod.DELETE])
def x_request_dict_json(request: "FixtureRequest[HttpMethod]") -> Tuple[str, Request]:
    return request.param.value, Request(
        method=request.param,
        path="/put/some/data/here",
        headers=(
            Header(name="ServiceHeader", value="service-header", is_sensitive=False),
            Header(name="RequestHeader", value="request-header", is_sensitive=False),
        ),
        params={"please": True, "carefully": True},
        json={"param1": 1, "param2": 2},
    )


@pytest.fixture
def x_sent_request_dict_json(x_request_dict_json) -> Tuple[str, SentRequest]:
    return x_request_dict_json[0], SentRequest(
        request=x_request_dict_json[1],
        base_url="https://example.com:4321",
        headers=(
            Header(name="ServiceHeader", value="service-header", is_sensitive=False),
            Header(name="RequestHeader", value="request-header", is_sensitive=False),
            Header(name="Content-Type", value="application/json", is_sensitive=False),
        ),
        body=b'{"param1": 1, "param2": 2}',
        proxies={"http://": "http://10.10.1.10:3128"},
    )


@pytest.fixture(params=[HttpMethod.POST, HttpMethod.PATCH, HttpMethod.PUT, HttpMethod.DELETE])
def x_request_list_json(request: "FixtureRequest[HttpMethod]") -> Tuple[str, Request]:
    return request.param.value, Request(
        method=request.param,
        path="/put/some/data/here",
        headers=(
            Header(name="ServiceHeader", value="service-header", is_sensitive=False),
            Header(name="RequestHeader", value="request-header", is_sensitive=False),
        ),
        params={"please": True, "carefully": True},
        json=[
            {"param1": 1, "param2": 2},
            {"param3": 3, "param4": 4},
        ],
    )


@pytest.fixture(params=[HttpMethod.POST, HttpMethod.PATCH, HttpMethod.PUT, HttpMethod.DELETE])
def x_custom_request_json(request: "FixtureRequest[HttpMethod]") -> Tuple[str, Request]:
    return request.param.value, Request(
        method=request.param,
        path="/put/some/data/here",
        headers=(
            Header(name="ServiceHeader", value="service-header", is_sensitive=False),
            Header(name="RequestHeader", value="request-header", is_sensitive=False),
        ),
        params={"please": True, "carefully": True},
        json={
            "param1": 1,
            "param2": 2,
            "time": date(2023, 7, 17),
            "decimal": Decimal("0.5656"),
        },
    )


@pytest.fixture(params=[HttpMethod.POST, HttpMethod.PATCH, HttpMethod.PUT, HttpMethod.DELETE])
def x_request_file(request: "FixtureRequest[HttpMethod]", test_file: BinaryIO) -> Tuple[str, Request]:
    return request.param.value, Request(
        method=request.param,
        path="/put/some/data/here",
        headers=(
            Header(name="ServiceHeader", value="service-header", is_sensitive=False),
            Header(name="RequestHeader", value="request-header", is_sensitive=False),
            Header(name="Content-Type", value="multipart/form-data; boundary=secretboundary", is_sensitive=False),
        ),
        params={"please": True, "carefully": True},
        body="Stallone is a Woman",
        files={"upload-file": test_file},
    )


@pytest.fixture
def patch_request() -> Request:
    return Request(
        method=HttpMethod.PATCH,
        path="/put/some/data/here",
        headers=(
            Header(name="ServiceHeader", value="service-header", is_sensitive=False),
            Header(name="RequestHeader", value="request-header", is_sensitive=False),
        ),
        params={"please": True, "carefully": True},
        body="It always seems impossible until it's done.",
    )


@pytest.fixture
def service() -> DummyService:
    return DummyService(
        headers=(Header(name="ServiceHeader", value="service-header", is_sensitive=False),),
        transport=HttpxTransport(base_url="https://example.com:4321", proxies={"http://": "http://10.10.1.10:3128"}),
    )


@pytest.fixture
def custom_json_encoder() -> Type[CustomJSONEncoder]:
    return CustomJSONEncoder


@pytest.fixture
def filtered_and_masked_headers() -> Set[Header]:
    return {
        Header(
            name="VeryClassBasedHeaderSens",
            value="idkfa",
            is_sensitive=True,
            create_mask=lambda value: f"...{value[::-1]}",
        ),
        Header(name="ClassBasedHeader", value="idkfa", is_sensitive=False, create_mask=None),
        Header(name="ClassBasedHeaderSens", value="idkfa", is_sensitive=True, create_mask=None),
        Header(name="Authorization", value="idkfa", is_sensitive=True, create_mask=None),
    }


@pytest.fixture
def test_file():
    file_path = os.path.join(os.path.dirname(__file__), "fixtures", "test.csv")
    return open(file_path, "rb")
