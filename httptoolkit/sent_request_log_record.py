from httptoolkit.sent_request import SentRequest


class RequestLogRecord:
    _METHOD_TEMPLATES = {"get": "Sending {method} {url}"}
    _DEFAULT_TEMPLATE = "Sending {method} {url} (body: {body_size})"

    def __init__(self, request: SentRequest) -> None:
        self._request = request

    def __str__(self) -> str:
        return self._template.format(**self.args())

    @property
    def _url(self) -> str:
        return self._request.url

    def args(self) -> dict:
        return {
            "method": self._request.method.upper(),
            "url": self._url,
            "headers": "\n".join(str(header) for header in self._request.headers),
            "body_size": 0 if not self._request.body else len(str(self._request.body)),
        }

    @property
    def _template(self) -> str:
        return self._METHOD_TEMPLATES.get(self._request.method.lower(), self._DEFAULT_TEMPLATE)
