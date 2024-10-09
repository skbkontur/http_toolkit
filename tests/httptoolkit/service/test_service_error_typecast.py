from unittest.mock import Mock

from httptoolkit.errors import HttpError, HttpErrorTypecast


def test_is_bad_request_error_when_not_service_error():
    error = Exception()
    assert HttpErrorTypecast.is_bad_request_error(error) is False


def test_is_bad_request_error_when_not_bad_request_error(get_request):
    response = Mock()
    response.status_code = 409

    error = HttpError(get_request, response)

    assert HttpErrorTypecast.is_bad_request_error(error) is False


def test_is_bad_request_error_when_bad_request_error(get_request):
    response = Mock()
    response.status_code = 400

    error = HttpError(get_request, response)

    assert HttpErrorTypecast.is_bad_request_error(error) is True
