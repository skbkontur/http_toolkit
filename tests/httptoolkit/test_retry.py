from datetime import datetime, timedelta
from email.utils import format_datetime

import pytest
from httpx import Request, Response as OriginalResponse, ConnectError, ConnectTimeout, ReadTimeout

from httptoolkit.retry import RetryManager


@pytest.fixture
def httpx_request() -> Request:
    return Request(method="GET", url="https://example.com:4321/")


@pytest.fixture
def retry_manager() -> RetryManager:
    return RetryManager(
        max_attempts=5,
        backoff_factor=0.01,
        exceptions=(ConnectError, ConnectTimeout),
        dont_retry_headers=("Another-Dont-Retry", "Dont-Retry"),
    )


@pytest.fixture
def retry_manager_with_more_exceptions() -> RetryManager:
    return RetryManager(
        max_attempts=5,
        backoff_factor=0.01,
        exceptions=(ConnectError, ConnectTimeout, ReadTimeout),
        dont_retry_headers="Dont-Retry",
    )


def test_retries(httpx_request: Request, retry_manager: RetryManager):
    retries = retry_manager.get_retries("GET")

    retry = next(retries)
    response = OriginalResponse(request=httpx_request, status_code=413)

    with retry:
        retry.process_response(response)

    assert retry.backoff == 0.01

    retry = next(retries)
    response = OriginalResponse(request=httpx_request, status_code=429, headers={"Retry-After": "1"})

    with retry:
        retry.process_response(response)

    assert retry.backoff == 1

    retry = next(retries)
    response = OriginalResponse(
        request=httpx_request,
        status_code=503,
        headers={"Retry-After": format_datetime(datetime.utcnow() + timedelta(seconds=1))},
    )

    with retry:
        retry.process_response(response)

    assert retry.backoff < 1

    retry = next(retries)
    response = OriginalResponse(request=httpx_request, status_code=413, headers={"Retry-After": "Invalid-Date"})

    with retry:
        retry.process_response(response)

    assert retry.backoff == 0.08

    retry = next(retries)
    response = OriginalResponse(request=httpx_request, status_code=429, headers={"Retry-After": ""})

    with retry:
        retry.process_response(response)

    assert retry.backoff == 0.16

    with pytest.raises(StopIteration):
        next(retries)


@pytest.mark.parametrize(
    "headers",
    (
        {},
        {"Another-Dont-Retry": ""},
        {"Another-Dont-Retry": "False"},
        {"Dont-Retry": ""},
        {"Dont-Retry": "False"},
    ),
)
def test_headers_do_retry(
    headers: dict,
    httpx_request: Request,
    retry_manager: RetryManager,
) -> None:
    retries = retry_manager.get_retries("GET")

    response = OriginalResponse(request=httpx_request, status_code=503, headers=headers)
    retry = next(retries)

    with pytest.raises(retry._RetryForResponseException) as e:
        retry.process_response(response)

    assert str(e.value) == "Service Unavailable"


@pytest.mark.parametrize(
    "headers",
    (
        {"Another-Dont-Retry": "True"},
        {"Dont-Retry": "True"},
    ),
)
def test_headers_dont_retry(
    headers: dict,
    httpx_request: Request,
    retry_manager: RetryManager,
) -> None:
    retries = retry_manager.get_retries("GET")

    response = OriginalResponse(request=httpx_request, status_code=503, headers=headers)
    retry = next(retries)

    retry.process_response(response)

    assert response.status_code == 503
    assert response.reason_phrase == "Service Unavailable"


def test_suppressed_exceptions():
    suppress_all = RetryManager(
        max_attempts=2,
        backoff_factor=1,
        exceptions=[Exception],
        dont_retry_headers="Dont-Retry",
    )
    suppress_nothing = RetryManager(
        max_attempts=2,
        backoff_factor=1,
        exceptions=(),
        dont_retry_headers="Dont-Retry",
    )

    with next(suppress_all.get_retries("GET")):
        raise Exception("Wasted")

    with pytest.raises(Exception):
        with next(suppress_nothing.get_retries("GET")):
            raise Exception("Wasted")
