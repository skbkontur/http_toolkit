from unittest.mock import Mock

import pytest

from httptoolkit.errors import ServiceError


def test_str_when_response_is_not_set(get_sent_request):
    error = ServiceError(get_sent_request)

    assert str(error) == "\n".join(
        [
            "Request: GET https://example.com:4321/put/some/data/here?please=True&carefully=True",
            "Request headers: {'ServiceHeader': 'service-header', 'RequestHeader': 'request-header'}",
            "Proxies: {'http://': 'http://10.10.1.10:3128'}",
        ]
    )


def test_str_when_response_is_set(get_sent_request):
    response = Mock()
    response.status_code = 401
    response.reason = "Unauthorized"
    response.text = "Invalid secret token"
    response.headers = {"go": "Away"}

    error = ServiceError(get_sent_request, response)

    assert str(error) == "\n".join(
        [
            "Request: GET https://example.com:4321/put/some/data/here?please=True&carefully=True",
            "Request headers: {'ServiceHeader': 'service-header', 'RequestHeader': 'request-header'}",
            "Proxies: {'http://': 'http://10.10.1.10:3128'}",
            "Response: 401 Unauthorized",
            "Response headers: {'go': 'Away'}",
            "Response body: Invalid secret token",
        ]
    )


def test_str_when_there_is_cause(get_sent_request):
    with pytest.raises(ServiceError) as error:
        try:
            raise Exception("original error message")
        except Exception as exc:
            raise ServiceError(get_sent_request) from exc

    assert str(error.value) == "\n".join(
        [
            "original error message",
            "Request: GET https://example.com:4321/put/some/data/here?please=True&carefully=True",
            "Request headers: {'ServiceHeader': 'service-header', 'RequestHeader': 'request-header'}",
            "Proxies: {'http://': 'http://10.10.1.10:3128'}",
        ]
    )


def test_response_code_when_response_is_set(get_sent_request):
    response = Mock()
    response.status_code = 401

    error = ServiceError(get_sent_request, response)

    assert error.response_code() == 401


def test_response_code_when_response_is_not_set(get_sent_request):
    error = ServiceError(get_sent_request)
    assert error.response_code() is None


def test_response_body_when_response_is_set(get_sent_request):
    response = Mock()
    response.text = "gladiolus"

    error = ServiceError(get_sent_request, response)

    assert error.response_body() == "gladiolus"


def test_response_body_when_response_is_not_set(get_sent_request):
    error = ServiceError(get_sent_request)
    assert error.response_body() is None


def test_error_context_if_no_cause(get_sent_request):
    with pytest.raises(ServiceError) as error:
        try:
            raise ConnectionError("no connection")
        except Exception:
            raise ServiceError(get_sent_request)

    assert "no connection" in str(error.value)
