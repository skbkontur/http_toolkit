import pytest
from pytest_httpx import HTTPXMock

from httptoolkit import Header, suppress_http_error, HttpMethod
from httptoolkit.errors import Error, ServiceError
from httptoolkit.request import Request
from httptoolkit.sent_request import SentRequest


def test_str_when_no_cause():
    error = Error("message")
    assert str(error) == "message"


def test_str_when_there_is_cause():
    with pytest.raises(Error) as error:
        try:
            raise RuntimeError("inner")
        except RuntimeError as exc:
            raise Error("outer") from exc

    assert str(error.value) == "RuntimeError: inner"


def test_str_when_there_is_context():
    with pytest.raises(Error) as error:
        try:
            raise RuntimeError("inner")
        except RuntimeError:
            raise Error("outer")

    assert str(error.value) == "RuntimeError: inner"


class TestServiceError:
    def test_dumps_filtered_and_masked_request_headers(self):
        sent_request = SentRequest(
            Request(
                method=HttpMethod.GET,
                path="/",
                headers=(),
                params={},
            ),
            headers=(
                Header(name="Authorization", value="auth.sid 123", is_sensitive=False),
                Header(name="RequestHeader", value="request-header", is_sensitive=False),
                Header(
                    name="MaskedRequestHeader",
                    value="masked-request-header",
                    is_sensitive=True,
                    create_mask=lambda value: f"...{value[-4:]}",
                ),
                Header(name="ServiceHeader", value="service-header", is_sensitive=False),
            ),
            base_url="https://example.com:4321",
            body=None,
        )

        error = ServiceError(sent_request)

        print(error)

        assert "'Authorization': '[filtered]'" in str(error)
        assert "'Authorization': 'auth.sid 123'" not in str(error)
        assert "'RequestHeader': 'request-header'" in str(error)
        assert "'MaskedRequestHeader': '...ader'" in str(error)


def test_suppress_http_error(service, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url="https://example.com:4321" + "/",
        status_code=404,
    )

    @suppress_http_error(404)
    def meth():
        service.get("/")

    def meth2():
        service.get("/")

    @suppress_http_error(400)
    def meth3():
        service.get("/")

    result = meth()
    assert result is None

    with pytest.raises(Error):
        meth2()

    with suppress_http_error(404):
        result = meth2()
        assert result is None

    with pytest.raises(Error):
        meth3()
