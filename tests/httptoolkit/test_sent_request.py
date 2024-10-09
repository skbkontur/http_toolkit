import pytest

from httptoolkit import Header, HttpMethod
from httptoolkit.request import Request
from httptoolkit.sent_request import SentRequest


def test_method(post_sent_request):
    assert post_sent_request.method == "POST"


def test_headers(x_sent_request_dict_json):
    metod, x_request = x_sent_request_dict_json
    assert set(x_request.headers) == {
        Header(name="ServiceHeader", value="service-header", is_sensitive=False),
        Header(name="RequestHeader", value="request-header", is_sensitive=False),
        Header(name="Content-Type", value="application/json", is_sensitive=False),
    }


def test_filtered_and_masked_headers(filtered_and_masked_headers):
    request = Request(
        method=HttpMethod.GET,
        path="/",
        headers=(),
        params={},
    )
    sent_request = SentRequest(
        request=request,
        base_url="",
        body=b"",
        headers=tuple(filtered_and_masked_headers),
    )
    assert set(sent_request.headers) == filtered_and_masked_headers

    assert sent_request.filtered_headers == {
        "ClassBasedHeader": "idkfa",
        "ClassBasedHeaderSens": "[filtered]",
        "VeryClassBasedHeaderSens": "...afkdi",
        "Authorization": "[filtered]",
    }


@pytest.mark.parametrize(
    "base_url,path",
    [
        ("https://example.com:4321/you", "put/some/data/here"),
        ("https://example.com:4321/you", "/put/some/data/here"),
        ("https://example.com:4321/you/", "put/some/data/here"),
        ("https://example.com:4321/you/", "/put/some/data/here"),
    ],
)
def test_url(base_url, path):
    request = SentRequest(
        Request(
            method=HttpMethod.POST,
            path=path,
            headers=(),
            params={},
            body=None,
        ),
        base_url=base_url,
        proxies={},
        body=None,
    )

    assert request.url == "https://example.com:4321/you/put/some/data/here"


def test_proxies(post_sent_request):
    assert post_sent_request.proxies == {
        "http://": "http://10.10.1.10:3128",
    }
