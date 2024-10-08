from typing import Dict, Optional, Tuple, Union

from httptoolkit.header import Header
from httptoolkit.request import Request


class SentRequest:
    def __init__(
        self,
        request: Request,
        base_url: str,
        body: Optional[Union[bytes, str]],
        proxies: Optional[Dict] = None,
        headers: Tuple[Header, ...] = (),
    ):
        self._request = request
        self._url = self._request.build_absolute_url(base_url)
        self._headers = headers
        self._body = body
        self._proxies = {} if proxies is None else proxies

    @property
    def url(self) -> str:
        return self._url

    @property
    def headers(self) -> Tuple[Header, ...]:
        return self._headers

    @property
    def filtered_headers(self) -> Dict[str, str]:
        headers = {header.name: header.filtered_value for header in self.headers}

        return headers

    @property
    def body(self) -> Optional[Union[bytes, str]]:
        return self._body

    @property
    def method(self) -> str:
        return self._request.method

    @property
    def proxies(self) -> Optional[dict]:
        return self._proxies
