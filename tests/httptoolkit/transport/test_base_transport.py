import pytest

from httptoolkit.transport import BaseHttpxTransport


def test_abstract_httpx_transport_cannot_instantiate():
    with pytest.raises(TypeError) as exception_info:
        BaseHttpxTransport(
            base_url="",
            allow_unverified_peer=False,
            open_timeout_in_seconds=1,
            read_timeout_in_seconds=1,
            retry_max_attempts=1,
            retry_backoff_factor=0,
            allow_post_retry=False,
            proxies={},
        )
    exception_message = str(exception_info.value)
    abstract_methods = ("_session_class",)
    print(exception_message)

    assert all(abstract_method in exception_message for abstract_method in abstract_methods)
