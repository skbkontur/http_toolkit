import pytest
from pytest_httpx import HTTPXMock

from httptoolkit import HttpxService
from httptoolkit.errors import ServiceError


class MyService(HttpxService):
    def __init__(self, key, *args, **kwargs):
        self.key = key
        super(MyService, self).__init__(url="https://example.com:4321/", *args, **kwargs)


@pytest.fixture
def stream_service():
    return MyService(key="fakecode")


@pytest.mark.parametrize("method", ("get", "post", "put", "patch"))
def test_stream_response_is_not_successful(
    method: str,
    stream_service,
    httpx_mock: HTTPXMock,
):
    httpx_mock.add_response(
        method=method.upper(),
        url="https://example.com:4321/api3/stat?key=fakecode",
        text="Param 'key' not specified or invalid",
        status_code=400,
    )

    service_method = getattr(stream_service, f"{method}_stream")

    with pytest.raises(ServiceError) as error:
        with service_method("api3/stat", params={"key": stream_service.key}):
            pass

    assert "Param 'key' not specified or invalid" in str(error.value)
