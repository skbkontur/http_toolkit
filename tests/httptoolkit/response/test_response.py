from datetime import timedelta
from unittest.mock import Mock

import pytest
from httpx import Response as OriginalResponse

from httptoolkit.response import Response


@pytest.fixture
def response():
    original_response = Mock(spec=OriginalResponse)

    original_response.ok = True
    original_response.status_code = 200
    original_response.reason_phrase = "OK"
    original_response.headers = {"ResponseHeader": "response-header"}
    original_response.content = b"Schwarzenegger is a woman!"
    original_response.text = "Schwarzenegger is a woman!"
    original_response.json.return_value = {"Foo": "bar"}
    original_response.elapsed = timedelta(182)

    return Response(original_response)


def test_ok(response):
    assert response.ok


def test_status_code(response):
    assert response.status_code == 200


def test_request_time(response):
    assert response.elapsed == timedelta(182)


def test_reason(response):
    assert response.reason == "OK"


def test_headers(response):
    assert response.headers == {"ResponseHeader": "response-header"}


def test_content(response):
    assert response.content == b"Schwarzenegger is a woman!"


def test_text(response):
    assert response.text == "Schwarzenegger is a woman!"


def test_json(response):
    assert response.json() == {"Foo": "bar"}
