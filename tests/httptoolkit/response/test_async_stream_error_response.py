import pytest
from pytest_httpx import HTTPXMock

from httptoolkit import AsyncHttpxService
from httptoolkit.errors import ServiceError


class MyAsyncService(AsyncHttpxService):
    def __init__(self, key, *args, **kwargs):
        self.key = key
        super(MyAsyncService, self).__init__(url="https://example.com:4321/", *args, **kwargs)


@pytest.fixture
def async_stream_service():
    return MyAsyncService(key="fakecode")


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ("get", "post", "put", "patch"))
async def test_async_stream_response_is_not_successful(
    method: str,
    async_stream_service,
    httpx_mock: HTTPXMock,
):
    httpx_mock.add_response(
        method=method.upper(),
        url="https://example.com:4321/api3/stat?key=fakecode",
        text="Param 'key' not specified or invalid",
        status_code=400,
    )

    async_service_method = getattr(async_stream_service, f"{method}_stream")

    with pytest.raises(ServiceError) as error:
        async with async_service_method("api3/stat", params={"key": async_stream_service.key}):
            pass

    assert "Param 'key' not specified or invalid" in str(error.value)
