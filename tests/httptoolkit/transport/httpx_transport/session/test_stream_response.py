from datetime import timedelta

import pytest
from httpx import ByteStream, Request as OriginalRequest, ConnectError, ConnectTimeout
from pytest_httpx import HTTPXMock

from httptoolkit.response import StreamResponse
from httptoolkit.retry import RetryManager
from httptoolkit.transport._httpx._session._sync import HttpxSession


@pytest.fixture
def session():
    return HttpxSession(
        retry_manager=RetryManager(
            max_attempts=5,
            backoff_factor=0.01,
            exceptions=(ConnectError, ConnectTimeout),
            dont_retry_headers="Dont-Retry",
        )
    )


@pytest.mark.parametrize("method", ("GET", "POST", "PUT", "DELETE", "PATCH"))
def test_stream_response(
    method: str,
    session: HttpxSession,
    httpx_mock: HTTPXMock,
):
    response_text = "first line\nsecond line\n"
    url = "http://example.com/foo/bar"

    httpx_mock.add_response(
        method=method.upper(),
        url=url,
        stream=ByteStream(response_text.encode("utf8")),
    )

    with session.stream(OriginalRequest(method, url)) as httpx_response:
        stream_response = StreamResponse(httpx_response)
        assert stream_response.status_code == 200
        assert [chunk for chunk in stream_response.iter_text(7)] == ["first l", "ine\nsec", "ond lin", "e\n"]
        assert stream_response.elapsed > timedelta(0)

    with session.stream(OriginalRequest(method, url)) as httpx_response:
        stream_response = StreamResponse(httpx_response)
        assert stream_response.status_code == 200
        assert [chunk for chunk in stream_response.iter_bytes(7)] == [b"first l", b"ine\nsec", b"ond lin", b"e\n"]
        assert stream_response.elapsed > timedelta(0)

    with session.stream(OriginalRequest(method, url)) as httpx_response:
        stream_response = StreamResponse(httpx_response)
        assert stream_response.status_code == 200
        assert [chunk for chunk in stream_response.iter_lines()] == ["first line", "second line"]
        assert stream_response.elapsed > timedelta(0)

    with session.stream(OriginalRequest(method, url)) as httpx_response:
        stream_response = StreamResponse(httpx_response)
        assert stream_response.status_code == 200
        assert [chunk for chunk in stream_response.iter_raw(7)] == [b"first l", b"ine\nsec", b"ond lin", b"e\n"]
        assert stream_response.elapsed > timedelta(0)

    with session.stream(OriginalRequest(method, url)) as httpx_response:
        stream_response = StreamResponse(httpx_response)
        assert stream_response.status_code == 200
        assert stream_response.read().decode("utf8") == response_text
        assert stream_response.elapsed > timedelta(0)


@pytest.mark.parametrize("method", ("GET", "POST", "PUT", "DELETE", "PATCH"))
def test_elapsed_not_available_until_closed(
    method: str,
    session: HttpxSession,
    httpx_mock: HTTPXMock,
):
    response_text = "first line\nsecond line\n"
    url = "http://example.com/foo/bar"

    httpx_mock.add_response(
        method=method.upper(),
        url=url,
        stream=ByteStream(response_text.encode("utf8")),
    )

    with session.stream(OriginalRequest(method, url)) as httpx_response:
        stream_response = StreamResponse(httpx_response)
        assert stream_response.status_code == 200
        with pytest.raises(RuntimeError) as error:
            stream_response.elapsed
        assert str(error.value) == "'.elapsed' may only be accessed after the response has been read or closed."
