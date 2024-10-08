import logging
from abc import abstractmethod, ABC
from contextlib import contextmanager
from typing import Any, Callable, Iterator, List, Optional, Tuple, Type, Union, Iterable

from httpx import Request as OriginalRequest, ConnectError, ConnectTimeout

from httptoolkit.encoder import default_json_encoder
from httptoolkit.errors import TransportError
from httptoolkit.header import Header
from httptoolkit.request import Request
from httptoolkit.retry import RetryManager
from httptoolkit.sent_request import SentRequest
from httptoolkit.sent_request_log_record import RequestLogRecord


class BaseHttpxTransport(ABC):
    DEFAULT_EXCEPTIONS = (ConnectError, ConnectTimeout)
    DEFAULT_DONT_RETRY_HEADERS = "Dont-Retry"
    DEFAULT_ALLOW_UNVERIFIED_PEER = False
    DEFAULT_TIMEOUT_IN_SECONDS = 1
    DEFAULT_RETRY_MAX_ATTEMPTS = 10
    DEFAULT_RETRY_BACKOFF_FACTOR = 0.1
    DEFAULT_ALLOW_POST_RETRY = False

    def __init__(
        self,
        base_url: str,
        allow_unverified_peer: bool = DEFAULT_ALLOW_UNVERIFIED_PEER,
        open_timeout_in_seconds: float = DEFAULT_TIMEOUT_IN_SECONDS,
        read_timeout_in_seconds: float = DEFAULT_TIMEOUT_IN_SECONDS,
        retry_max_attempts: int = DEFAULT_RETRY_MAX_ATTEMPTS,
        retry_backoff_factor: float = DEFAULT_RETRY_BACKOFF_FACTOR,
        allow_post_retry: bool = DEFAULT_ALLOW_POST_RETRY,
        proxies: Optional[dict] = None,
        json_encoder: Callable[[Any], str] = default_json_encoder,
        retry_status_codes: Iterable[int] = RetryManager.DEFAULT_STATUS_CODES,
    ) -> None:
        if proxies is None:
            proxies = {}
        method_whitelist = RetryManager.DEFAULT_METHODS

        if allow_post_retry:
            method_whitelist |= {"POST"}

        self._base_url = base_url
        self._open_timeout_in_seconds = open_timeout_in_seconds
        self._read_timeout_in_seconds = read_timeout_in_seconds
        self._proxies = proxies
        self._session = self._session_class(
            retry_manager=RetryManager(
                exceptions=self.DEFAULT_EXCEPTIONS,
                max_attempts=retry_max_attempts,
                backoff_factor=retry_backoff_factor,
                methods=method_whitelist,
                dont_retry_headers=self.DEFAULT_DONT_RETRY_HEADERS,
                status_codes=retry_status_codes,
            ),
            allow_unverified_peer=allow_unverified_peer,
            proxies=self._proxies,
        )
        self._logger = logging.getLogger(self.__class__.__module__)
        self._json_encoder = json_encoder

    @property
    @abstractmethod
    def _session_class(self) -> Type[Any]:  # pragma: no cover
        pass

    def _build_httpx_request(
        self,
        request: Request,
    ) -> OriginalRequest:
        headers, content, data = self._prepare_content(request)
        dict_headers = {header.name.lower(): header.value for header in headers + request.headers}
        httpx_request = self._session.build_request(
            method=request.method,
            url=request.build_absolute_url(self._base_url),
            headers=dict_headers,
            content=content,
            files=request.files,
            data=data,
            extensions={
                "timeout": {
                    "connect": self._open_timeout_in_seconds,
                    "read": self._read_timeout_in_seconds,
                    "write": None,
                    "pool": None,
                }
            },
        )
        return httpx_request

    @contextmanager
    def _managed_session(self, request: SentRequest) -> Iterator[Any]:
        self._log(request)

        try:
            yield self._session

        except Exception as exc:
            raise TransportError(request) from exc

    def _encode_json(self, request_json: Union[dict, List]) -> Tuple[Tuple[Header, ...], Union[bytes, str]]:
        body = self._json_encoder(request_json)
        headers = (Header(name="Content-Type", value="application/json", is_sensitive=False),)
        return headers, body

    def _prepare_content(
        self,
        request: Request,
    ) -> Tuple[Tuple[Header, ...], Optional[Union[bytes, str]], Optional[dict]]:
        if request.files is not None:
            if request.json is not None:
                raise RuntimeError("json and files can't be sent together")
            if request.body is not None:
                return (), None, {"data": request.body}
            return (), None, None
        if request.json is not None:
            if request.body is not None:
                raise RuntimeError("json and body can't be sent together")
            return *self._encode_json(request.json), None
        return (), request.body, None

    def _prepare_sent_request(
        self,
        request: Request,
        httpx_request: OriginalRequest,
    ) -> SentRequest:
        set_headers_with_sensitive = {header.name.lower(): header.is_sensitive for header in request.headers}
        httpx_request.read()
        content = httpx_request.content
        httpx_headers = tuple(
            Header(
                name=header_name,
                value=httpx_request.headers[header_name],
                is_sensitive=set_headers_with_sensitive.get(header_name, False),
            )
            for header_name in httpx_request.headers
        )
        return SentRequest(
            request=request, base_url=self._base_url, body=content, proxies=self._proxies, headers=httpx_headers
        )

    def _log(self, request: SentRequest) -> None:
        request_log_record = RequestLogRecord(request)
        self._logger.info(request_log_record, extra=request_log_record.args())
