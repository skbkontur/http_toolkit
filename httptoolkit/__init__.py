import logging

from httptoolkit.errors import ServiceError, suppress_http_error
from httptoolkit.header import AuthSidHeader, BasicAuthHeader, BearerAuthHeader, Header
from httptoolkit.service import AsyncService, Service
from httptoolkit.httpx_service import HttpxService, AsyncHttpxService
from httptoolkit.http_method import HttpMethod

__all__ = [
    "Service",
    "AsyncService",
    "HttpxService",
    "AsyncHttpxService",
    "ServiceError",
    "suppress_http_error",
    "Header",
    "AuthSidHeader",
    "BasicAuthHeader",
    "BearerAuthHeader",
    "HttpMethod",
]

logger = logging.getLogger("httptoolkit")
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.INFO)
httpx_log = logging.getLogger("httpx")
httpx_log.propagate = False
