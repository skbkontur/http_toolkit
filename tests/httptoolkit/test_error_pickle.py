import pickle

from httptoolkit import HttpxService, HttpMethod
import pytest
from pytest_httpx import HTTPXMock
from httptoolkit.errors import ServiceError
from httptoolkit.request import Request
from httptoolkit.sent_request import SentRequest


class TestChaining:
    class Error(Exception):
        def __str__(self):
            return f"{self.__context__}\n{super().__str__()}" if self.__context__ else super().__str__()

    @pytest.fixture()
    def sent_request_object(self):
        return SentRequest(
            Request(method=HttpMethod.GET, path="/", params={}), base_url="base-url", proxies={}, body=None
        )

    def test_collects_context(self, sent_request_object):
        with pytest.raises(ServiceError) as service_error:
            try:
                raise self.Error("First")
            except Exception:
                try:
                    raise self.Error("Second")
                except Exception:
                    raise ServiceError(sent_request_object)

        pickled_error = str(pickle.loads(pickle.dumps(service_error.value)))
        assert "Second" in pickled_error
        assert "First" in pickled_error

    def test_collects_cause(self, sent_request_object):
        chain = None
        try:
            raise self.Error("First")
        except Exception as e:
            chain = e
        try:
            raise self.Error("Second") from chain
        except Exception as e:
            chain = e

        with pytest.raises(ServiceError) as service_error:
            raise ServiceError(sent_request_object) from chain

        pickled_error = str(pickle.loads(pickle.dumps(service_error.value)))
        assert "Second" in pickled_error
        assert "First" in pickled_error


class MyService(HttpxService):
    def __init__(self, key, *args, **kwargs):
        self.key = key
        super(MyService, self).__init__(url="https://example.com:4321/", *args, **kwargs)


@pytest.fixture
def pickle_service():
    return MyService(key="fakecode")


@pytest.mark.parametrize("method", ("get", "post", "put", "patch"))
def test_stream_response_pickle_error(
    method: str,
    pickle_service,
    httpx_mock: HTTPXMock,
):
    httpx_mock.add_response(
        method=method.upper(),
        url="https://example.com:4321/api3/stat?key=fakecode",
        text="Param 'key' not specified or invalid",
        status_code=400,
    )

    service_method = getattr(pickle_service, f"{method}_stream")

    with pytest.raises(ServiceError) as error:
        with service_method("api3/stat", params={"key": pickle_service.key}):
            pass

    file = pickle.dumps(error.value)
    pickled_error = str(pickle.loads(file))
    assert f"HttpError: Request: {method.upper()} https://example.com:4321/api3/stat?key=fakecode" in pickled_error
    assert "Response: 400 Bad Request" in pickled_error
    assert "Response body: Param 'key' not specified or invalid" in pickled_error


@pytest.mark.parametrize("method", ("get", "post", "put", "patch"))
def test_response_pickle_error(
    method: str,
    pickle_service,
    httpx_mock: HTTPXMock,
):
    httpx_mock.add_response(
        method=method.upper(),
        url="https://example.com:4321/api3/stat?key=fakecode",
        text="Param 'key' not specified or invalid",
        status_code=400,
    )

    service_method = getattr(pickle_service, f"{method}")

    with pytest.raises(ServiceError) as error:
        service_method("api3/stat", params={"key": pickle_service.key})

    file = pickle.dumps(error.value)
    pickled_error = str(pickle.loads(file))
    assert f"Request: {method.upper()} https://example.com:4321/api3/stat?key=fakecode" in pickled_error
    assert "Response: 400 Bad Request" in pickled_error
    assert "Response body: Param 'key' not specified or invalid" in pickled_error
