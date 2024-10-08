## Transport

The configured transport is passed to the Service. HttpxTransport is an out-of-the-box implementation of an httpx-based transport, an instance of which you can pass to the Service.
## Example

```python

from httptoolkit import Service, Header
from httptoolkit.transport import HttpxTransport


class DummyService(Service):
    pass


DummyService(
    headers=(Header(name="ServiceHeader", value="service-header", is_sensitive=False),),
    transport=HttpxTransport(
        base_url="https://example.com:4321",
        proxies={"http://": "http://10.10.1.10:3128"},
        # allow_unverified_peer: bool = DEFAULT_ALLOW_UNVERIFIED_PEER,
        # open_timeout_in_seconds: float = DEFAULT_TIMEOUT_IN_SECONDS,
        # read_timeout_in_seconds: float = DEFAULT_TIMEOUT_IN_SECONDS,
        # retry_max_attempts: int = DEFAULT_RETRY_MAX_ATTEMPTS,
        # retry_backoff_factor: float = DEFAULT_RETRY_BACKOFF_FACTOR,
        # allow_post_retry: bool = True,
        # json_encoder: Callable[[Any], str] = default_json_encoder,
    ),
    ## base_url in this case is passed to transport
)
```

## Custom Transport

You can pass an instance of your own Transport class to Service by inheriting from the base class (Sync -> BaseTransport, Async -> BaseAsyncTransport)
```python
from typing import Tuple, Iterator
from httptoolkit import Service, Header
from httptoolkit.response import Response, StreamResponse
from httptoolkit.request import Request
from httptoolkit.sent_request import SentRequest
from httptoolkit.transport import BaseTransport


class DummyService(Service):
    pass


class DummyTransport(BaseTransport):

    def send(self, request: Request) -> Tuple[SentRequest, Response]:
        pass

    def stream(self, request: Request) -> Iterator[Tuple[SentRequest, StreamResponse]]:
        pass


DummyService(
    headers=(Header(name="ServiceHeader", value="service-header", is_sensitive=False),),
    transport=DummyTransport(
        # ...
    ),
)
```

To customize retries in your own Transport class, you can use the RetryManager class

```python
from contextlib import contextmanager
from typing import Iterator

from httptoolkit.response import Response, StreamResponse
from httptoolkit.request import Request
from httptoolkit.transport import BaseTransport
from httptoolkit.retry import RetryManager


class DummyTransport(BaseTransport):
    DEFAULT_EXCEPTIONS = (Exception1, Exception2)
    DEFAULT_ALLOW_UNVERIFIED_PEER = False
    DEFAULT_TIMEOUT_IN_SECONDS = 1
    DEFAULT_RETRY_MAX_ATTEMPTS = 10
    DEFAULT_RETRY_BACKOFF_FACTOR = 0.1
    DEFAULT_ALLOW_POST_RETRY = False
    DEFAULT_DONT_RETRY_HEADERS = "Dont-Retry"

    def __init__(
            self,
            retry_max_attempts: int = DEFAULT_RETRY_MAX_ATTEMPTS,
            retry_backoff_factor: float = DEFAULT_RETRY_BACKOFF_FACTOR,
            allow_post_retry: bool = DEFAULT_ALLOW_POST_RETRY,
    ) -> None:
        method_whitelist = RetryManager.DEFAULT_METHODS
        if allow_post_retry:
            method_whitelist |= {"POST"}
        self.retry_manager = RetryManager(
            exceptions=self.DEFAULT_EXCEPTIONS,
            max_attempts=retry_max_attempts,
            backoff_factor=retry_backoff_factor,
            methods=method_whitelist,
            dont_retry_headers=self.DEFAULT_DONT_RETRY_HEADERS,
        )

    def send(self, request: Request) -> Response:
        for retry in self._retry_manager.get_retries(request.method):
            with retry:
                response =  ## get a response
                retry.process_response(response)
                return response

            # noinspection PyUnreachableCode
            time.sleep(retry.backoff)

    @contextmanager
    def stream(self, request: Request) -> Iterator[StreamResponse]:
        response = self.send(request)
        try:
            yield response
        finally:
            response.close()
```