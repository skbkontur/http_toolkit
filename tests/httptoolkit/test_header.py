import pytest

from httptoolkit import Header, header
from httptoolkit.header import KnownSensitiveHeaders


class TestKnownSensitiveHeaders:
    def test_add(self):
        assert KnownSensitiveHeaders().add("ß").add("ß").items == {"ss"}

    def test_update(self):
        assert KnownSensitiveHeaders().update(["ß", "ß"]).update(["ß", "ß"]).items == {"ss"}

    def test_in(self):
        assert "ß" in KnownSensitiveHeaders(["ß"])


def test_auth_headers():
    auth_sid_header = header.AuthSidHeader("foo")
    assert auth_sid_header.name == "Authorization"
    assert auth_sid_header.value == "auth.sid foo"
    assert auth_sid_header.is_sensitive is True

    basic_auth_header = header.BasicAuthHeader(username="auth@example.ru", password="password")
    assert basic_auth_header.name == "Authorization"
    assert basic_auth_header.value == "Basic YXV0aEBleGFtcGxlLnJ1OnBhc3N3b3Jk"
    assert basic_auth_header.is_sensitive is True

    auth_sid_header = header.BearerAuthHeader("42")
    assert auth_sid_header.name == "Authorization"
    assert auth_sid_header.value == "Bearer 42"
    assert auth_sid_header.is_sensitive is True


def test_string_representation_of_headers():
    headers = [
        Header(name="ClassBasedHeader", value="idkfa", is_sensitive=False),
        Header(name="ClassBasedHeaderSens", value="idkfa", is_sensitive=True),
        Header(name="ClassBasedReqHeader", value="idkfa", is_sensitive=False),
        Header(name="ClassBasedReqHeaderSens", value="idkfa", is_sensitive=True),
        Header(name="RequestHeader", value="request-header", is_sensitive=False),
        Header(name="ServiceHeader", value="service-header", is_sensitive=False),
        Header(name="authorization", value="idkfa", is_sensitive=True),
        Header(name="myPasswordHeader", value="idkfa", is_sensitive=True),
        Header(name="topSecretHeader", value="idkfa", is_sensitive=True),
    ]

    string_headers = list(map(str, headers))

    assert string_headers == [
        "ClassBasedHeader: idkfa",
        "ClassBasedHeaderSens: [filtered]",
        "ClassBasedReqHeader: idkfa",
        "ClassBasedReqHeaderSens: [filtered]",
        "RequestHeader: request-header",
        "ServiceHeader: service-header",
        "authorization: [filtered]",
        "myPasswordHeader: [filtered]",
        "topSecretHeader: [filtered]",
    ]


def test_masked_representation_of_headers():
    headers = [
        Header(
            name="ClassBasedHeader",
            value="idkfadasd",
            is_sensitive=True,
            create_mask=lambda value: value[1:3],
        ),
        Header(
            name="ClassBasedHeaderSens",
            value="idkfadasd",
            is_sensitive=True,
            create_mask=lambda value: value[-4:],
        ),
        Header(
            name="ClassBasedReqHeader",
            value="idkfadasd",
            is_sensitive=True,
            create_mask=lambda value: value[-4:],
        ),
        Header(
            name="ClassBasedReqHeaderSens",
            value="idkfadas",
            is_sensitive=True,
            create_mask=lambda value: value[:-3],
        ),
        Header(
            name="RequestHeader",
            value="request-header",
            is_sensitive=True,
            create_mask=lambda value: value[2:6],
        ),
        Header(
            name="ServiceHeader",
            value="service-header",
            is_sensitive=True,
            create_mask=lambda value: value[::2],
        ),
        Header(
            name="authorization", value="idkfadsad", is_sensitive=True, create_mask=lambda value: f"...{value[::-1]}"
        ),
        Header(
            name="myPasswordHeader", value="idkfadasd", is_sensitive=True, create_mask=lambda value: f"...{value[-4:]}"
        ),
        Header(
            name="topSecretHeader", value="idkfadasd", is_sensitive=True, create_mask=lambda value: f"...{value[-4:]}"
        ),
    ]

    string_masked_headers = list(map(str, headers))
    assert string_masked_headers == [
        "ClassBasedHeader: dk",
        "ClassBasedHeaderSens: dasd",
        "ClassBasedReqHeader: dasd",
        "ClassBasedReqHeaderSens: idkfa",
        "RequestHeader: ques",
        "ServiceHeader: sriehae",
        "authorization: ...dasdafkdi",
        "myPasswordHeader: ...dasd",
        "topSecretHeader: ...dasd",
    ]

    with pytest.raises(RuntimeError) as error:
        Header(name="ServiceHeader", value="service-header", is_sensitive=False, create_mask=lambda value: value[::2])
    assert (
        str(error.value)
        == "'.mask' may only be set if is_sensitive = True\nor name is in KNOWN_SENSITIVE_HEADERS_NAMES"
    )


def test_masked_representation_auth_headers():
    masked_auth_sid_header = header.AuthSidHeader("foooooo", create_mask=lambda value: value[4:12])
    assert str(masked_auth_sid_header) == "Authorization: .sid foo"

    masked_basic_auth_header = header.BasicAuthHeader(
        username="auth@example.ru", password="password", create_mask=lambda value: value[1:3]
    )
    assert str(masked_basic_auth_header) == "Authorization: as"

    masked_auth_sid_header = header.BearerAuthHeader("42", create_mask=lambda value: value[::-1])
    assert str(masked_auth_sid_header) == "Authorization: 24 reraeB"
