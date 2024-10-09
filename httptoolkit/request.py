from typing import Dict, List, Optional, Tuple, Union, BinaryIO
from urllib.parse import urlencode

from httptoolkit.header import Header
from httptoolkit.http_method import HttpMethod


class Request:
    def __init__(
        self,
        method: HttpMethod,
        path: str,
        params: Optional[dict],
        headers: Tuple[Header, ...] = (),
        body: Optional[Union[bytes, str]] = None,
        json: Optional[Union[dict, List]] = None,
        files: Optional[Dict[str, Union[BinaryIO, Tuple[str, BinaryIO, str]]]] = None,
    ):
        params = params if params is not None else {}

        self._headers: Tuple[Header, ...] = headers

        self._method = method
        self._path = path
        self._params = params
        self._body = body
        self._json = json
        self._files = files

    def build_absolute_url(self, base_url: str) -> str:
        return "/".join((base_url.rstrip("/"), self.full_path.lstrip("/")))

    @property
    def full_path(self) -> str:
        if not self.params:
            return self.path
        else:
            return f"{self.path}?{urlencode(self.params)}"

    def set_new_headers(self, new_headers: Tuple[Header, ...]) -> "Request":
        return Request(
            method=self._method,
            path=self.path,
            params=self.params,
            headers=self.headers + new_headers,
            body=self.body,
            json=self.json,
            files=self.files,
        )

    @property
    def headers(self) -> Tuple[Header, ...]:
        """
        :return: All service and request headers combined into a single tuple.
        """
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
        return self._method.value

    @property
    def path(self) -> str:
        return self._path

    @property
    def params(self) -> Optional[dict]:
        return self._params

    @property
    def json(self) -> Optional[Union[dict, List]]:
        return self._json

    @property
    def files(self) -> Optional[Dict[str, Union[BinaryIO, Tuple[str, BinaryIO, str]]]]:
        return self._files
