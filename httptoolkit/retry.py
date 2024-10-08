import re
import time
from contextlib import suppress
from email.utils import mktime_tz, parsedate_tz
from typing import FrozenSet, Iterable, Iterator, Optional, Type

from httptoolkit.response import OriginalResponse


class Retry(suppress):
    class _RetryForResponseException(Exception):
        def __init__(self, response: OriginalResponse) -> None:
            super().__init__(response.reason_phrase)

    def __init__(
        self,
        ist_last: bool,
        backoff: float,
        exceptions: Iterable[Type[Exception]],
        status_codes: FrozenSet[int],
        dont_retry_headers: Iterable[str],
    ) -> None:
        super().__init__(self._RetryForResponseException, *exceptions)

        self._status_codes = status_codes
        self._dont_retry_headers = dont_retry_headers
        self._is_last = ist_last
        self._backoff = backoff
        self._response_backoff = 0.0

    @property
    def backoff(self) -> float:
        return self._response_backoff or self._backoff

    def process_response(self, response: OriginalResponse) -> None:
        response_headers = response.headers
        dont_retry = "false"
        for dont_retry_header in self._dont_retry_headers:
            if response_headers.get(dont_retry_header, "").lower() == "true":
                dont_retry = "true"
                break
        if dont_retry == "true":
            return

        if not self._is_last and response.status_code in self._status_codes:
            self._response_backoff = self._parse_retry_header(response_headers.get("Retry-After", ""))
            raise self._RetryForResponseException(response)

        return

    @staticmethod
    def _parse_retry_header(value: str) -> float:
        if not value:
            return 0

        # Whitespace: https://tools.ietf.org/html/rfc7230#section-3.2.4
        if re.match(r"^\s*[0-9]+\s*$", value):
            return max(0, int(value))

        retry_date_tuple = parsedate_tz(value)

        if retry_date_tuple is None:
            return 0

        retry_date = mktime_tz(retry_date_tuple)

        return max(0, retry_date - time.time())

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        return not self._is_last and super().__exit__(exc_type, exc_val, exc_tb)


class RetryManager:
    DEFAULT_METHODS = frozenset(["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"])
    DEFAULT_STATUS_CODES = frozenset([413, 429, 503])
    DEFAULT_BACKOFF_MAX = 120

    def __init__(
        self,
        max_attempts: int,
        backoff_factor: float,
        exceptions: Iterable[Type[Exception]],
        dont_retry_headers: Iterable[str],
        backoff_max: float = DEFAULT_BACKOFF_MAX,
        methods: Optional[Iterable[str]] = None,
        status_codes: Iterable[int] = DEFAULT_STATUS_CODES,
    ) -> None:
        self._max_attempts = max_attempts
        self._backoff_factor = backoff_factor
        self._backoff_max = backoff_max
        self._methods = frozenset(methods) if methods is not None else self.DEFAULT_METHODS
        self._status_codes = frozenset(status_codes)
        self._exceptions = exceptions
        self.dont_retry_headers = dont_retry_headers

    def _get_exponential_backoff(self, index: int) -> float:
        return min(self._backoff_max, self._backoff_factor * (2 ** (index - 1)))

    def _get_max_attempts_for_method(self, method: str) -> int:
        return self._max_attempts if method in self._methods else 1

    def get_retries(self, method: str) -> Iterator[Retry]:
        max_attempts = self._get_max_attempts_for_method(method)

        for index in range(1, max_attempts + 1):
            yield Retry(
                ist_last=index >= max_attempts,
                backoff=self._get_exponential_backoff(index),
                exceptions=self._exceptions,
                status_codes=self._status_codes,
                dont_retry_headers=self.dont_retry_headers,
            )
