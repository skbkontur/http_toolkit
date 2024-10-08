import pytest

from httptoolkit import AuthSidHeader, BasicAuthHeader, BearerAuthHeader, Header, HttpMethod
from httptoolkit.request import Request


def test_method(post_request):
    assert post_request.method == "POST"


def test_path(post_request):
    assert post_request.path == "/put/some/data/here"


def test_params(post_request):
    assert post_request.params == {"please": True, "carefully": True}


def test_headers(post_request):
    assert set(post_request.headers) == {
        Header(name="ServiceHeader", value="service-header", is_sensitive=False),
        Header(name="RequestHeader", value="request-header", is_sensitive=False),
    }


def test_set_new_headers(test_file):
    old_post_request = Request(
        method=HttpMethod.POST,
        path="/put/some/data/here",
        headers=(
            Header(name="ServiceHeader", value="service-header", is_sensitive=False),
            Header(name="RequestHeader", value="request-header", is_sensitive=False),
        ),
        params={"please": True, "carefully": True},
        body="It always seems impossible until it's done.",
        json={"param1": 1, "param2": 2},
        files={"upload-file": test_file},
    )
    new_post_request = old_post_request.set_new_headers(
        (
            Header(name="NewHeader1", value="new-header", is_sensitive=False),
            Header(name="NewHeader2", value="very-new-header", is_sensitive=False),
        )
    )
    assert old_post_request.headers == (
        Header(name="ServiceHeader", value="service-header", is_sensitive=False),
        Header(name="RequestHeader", value="request-header", is_sensitive=False),
    )

    assert new_post_request.method == "POST"
    assert new_post_request.path == "/put/some/data/here"
    assert new_post_request.headers == (
        Header(name="ServiceHeader", value="service-header", is_sensitive=False),
        Header(name="RequestHeader", value="request-header", is_sensitive=False),
        Header(name="NewHeader1", value="new-header", is_sensitive=False),
        Header(name="NewHeader2", value="very-new-header", is_sensitive=False),
    )
    assert new_post_request.params == {"please": True, "carefully": True}
    assert new_post_request.body == "It always seems impossible until it's done."
    assert new_post_request.json == {"param1": 1, "param2": 2}
    assert new_post_request.files == {"upload-file": test_file}


def test_filtered_and_masked_headers(filtered_and_masked_headers):
    request = Request(
        method=HttpMethod.GET,
        path="/",
        headers=tuple(filtered_and_masked_headers),
        params={},
    )

    assert set(request.headers) == filtered_and_masked_headers

    assert request.filtered_headers == {
        "ClassBasedHeader": "idkfa",
        "ClassBasedHeaderSens": "[filtered]",
        "VeryClassBasedHeaderSens": "...afkdi",
        "Authorization": "[filtered]",
    }


@pytest.mark.parametrize(
    "auth_header",
    (
        AuthSidHeader("123"),
        BasicAuthHeader(username="auth@example.ru", password="password"),
        BearerAuthHeader(value="42"),
    ),
)
def test_auth_headers(auth_header):
    request = Request(
        method=HttpMethod.GET,
        path="/",
        headers=(
            auth_header,
            Header(name="ServiceHeader", value="service-header", is_sensitive=False),
        ),
        params={},
    )

    assert request.filtered_headers == {
        "Authorization": "[filtered]",
        "ServiceHeader": "service-header",
    }


def test_body(post_request):
    assert post_request.body == "It always seems impossible until it's done."


def test_json(post_request):
    assert post_request.json is None


def test_json_present():
    x_request = Request(HttpMethod.POST, "/", {}, json={"param1": 1, "param2": 2})
    assert x_request.json == {"param1": 1, "param2": 2}


def test_files(post_request):
    assert post_request.files is None


def test_files_present(test_file):
    request = Request(HttpMethod.POST, "/", {}, files={"upload-file": test_file})
    assert request.files == {"upload-file": test_file}
