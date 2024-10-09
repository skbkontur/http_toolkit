# http_toolkit
The httptoolkit library is a tool for working with HTTP requests in Python that allows you to easily create, customize, and send requests to various services. It provides a simple interface for working with HTTP clients. The library also allows flexible transport customization and abstraction from a particular implementation of HTTP clients.

## HTTPXService

If you don't need to use a configured transport, use HTTPXService (for async -> AsyncHttpxService)

```python
from httptoolkit import HttpxService
from httptoolkit import Header

headers = (
    Header(name="My-Header", value="my-value", is_sensitive=False),
)
httpbin = HttpxService("http://httpbin.org", headers=headers)
httpbin.get("/get")
httpbin.post("/post")
```

## Service

If you want to use a configured transport, use Service. (Service -> HttpxTransport, AsyncService -> AsyncHttpxTransport)
```python
### Sync

from httptoolkit import Service, Header
from httptoolkit.transport import HttpxTransport


class DummyService(Service):
    pass


DummyService(
    headers=(Header(name="ServiceHeader", value="service-header", is_sensitive=False),),
    transport=HttpxTransport(base_url="https://example.com:4321", proxies={"http://": "http://10.10.1.10:3128"}),
    ## base_url in this case is passed to transport
)
```

```python
### Async

from httptoolkit import AsyncService, Header
from httptoolkit.transport import AsyncHttpxTransport


class DummyService(AsyncService):
    pass


DummyService(
    headers=(Header(name="ServiceHeader", value="service-header", is_sensitive=False),),
    transport=AsyncHttpxTransport(base_url="https://example.com:4321", proxies={"http://": "http://10.10.1.10:3128"}),
    ## base_url in this case is passed to transport
)
```

### Sending a request

```python

from httptoolkit import Service, Header, HttpMethod
from httptoolkit.transport import HttpxTransport
from httptoolkit.request import Request


class DummyService(Service):
    pass


service = DummyService(
    headers=(Header(name="ServiceHeader", value="service-header", is_sensitive=False),),
    transport=HttpxTransport(base_url="https://example.com:4321", proxies={"http://": "http://10.10.1.10:3128"}),
    ## base_url in this case is passed to transport
)

# By method
service.post(
    path="/somewhere",
    headers=(Header(name="SuperSecret", value="big_secret", is_sensitive=True, create_mask=lambda value: value[-4:]),),
    params={"over": "the rainbow"},
    body="Something",
)

# By request
service.request(Request(method=HttpMethod.POST, body="Request", params={}, path=""))
```

### Sending JSON and multipart-files

```python
from httptoolkit import Service, Header
from httptoolkit.transport import HttpxTransport


class DummyService(Service):
    pass


service = DummyService(
    headers=(Header(name="ServiceHeader", value="service-header", is_sensitive=False),),
    transport=HttpxTransport(base_url="https://example.com:4321", proxies={"http://": "http://10.10.1.10:3128"}),
    ## base_url in this case is passed to transport
)

# Send JSON (json_encoder is the default, but can be changed in transport)
# Do not send with body and files
service.post(
    path="/somewhere",
    headers=(Header(name="SuperSecret", value="big_secret", is_sensitive=True, create_mask=lambda value: value[-4:]),),
    params={"over": "the rainbow"},
    json={
        "param1": 1,
        "param2": 2,
    },
)

# Send multipart-files in the format Dict[str, Union[BinaryIO, Tuple[str, BinaryIO, str]]]
# Can be sent with body, but cannot be sent with json
service.post(
    path="/somewhere",
    headers=(Header(name="SuperSecret", value="big_secret", is_sensitive=True, create_mask=lambda value: value[-4:]),),
    params={"over": "the rainbow"},
    files={"upload-file": open("report.xls", "rb")},
    # different format files = {'upload-file': ('report.xls', open('report.xls', 'rb'), 'application/vnd.ms-excel')} 
)
```

## The name of the library logger

httptoolkit

## Default logging level

logging.INFO

## Example of logging settings

```python
import logging
import httptoolkit

logging.basicConfig(level="INFO")


class MyService(httptoolkit.HttpxService):
    def test(self):
        self.get("/")


service = MyService("https://test.ru")

service.test()
```
## Output
```python
INFO:httptoolkit.transport._sync:Sending GET https://test.ru/
```

All about Transport
- [HttpxTransport](https://github.com/skbkontur/http_toolkit/tree/master/docs/TRANSPORT.md#transport)
- [Creating your own Transport](https://github.com/skbkontur/http_toolkit/tree/master/docs/TRANSPORT.md#custom-transport)

OpenTelemetry
Allows using [OpenTelemetry HTTPX](https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation/opentelemetry-instrumentation-httpx) to add request tracing via [http_toolkit](https://github.com/skbkontur/http_toolkit) in case [HttpxTransport](https://github.com/skbkontur/http_toolkit/tree/master/docs/TRANSPORT.md#transport) is used.
