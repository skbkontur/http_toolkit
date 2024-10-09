from contextlib import contextmanager
from typing import Optional


class Error(Exception):
    def __str__(self):
        context = self.__cause__ or self.__context__

        if context:
            return "{}: {}".format(type(context).__name__, context)
        else:
            return super().__str__()


class TransportError(Error):
    def __init__(self, request) -> None:
        self.request = request


class ServiceError(Error):
    MESSAGE_DELIMITER = "\n"

    def __init__(self, request, response=None):
        self._request = request
        self._response = response

    def __str__(self):
        description = self._description()
        context = self.__cause__ or self.__context__

        if context:
            description = self._concatenate(str(context), description)

        return description

    @property
    def response(self):
        return self._response

    def response_code(self) -> Optional[int]:
        if self._response is not None:
            return self._response.status_code
        return None

    def response_body(self) -> Optional[str]:
        if self._response is not None:
            return self._response.text
        return None

    def _description(self):
        return self._concatenate(self._request_description(), self._response_description())

    def _request_description(self):
        return self._concatenate(
            "Request: {} {}".format(self._request.method.upper(), self._request.url),
            "Request headers: {}".format(self._request.filtered_headers),
            "Proxies: {}".format(self._request.proxies),
        )

    def _response_description(self):
        if self._response is not None:
            return self._concatenate(
                "Response: {} {}".format(self.response_code(), self._response.reason),
                "Response headers: {}".format(self._response.headers),
                "Response body: {}".format(self.response_body()),
            )

    def __getstate__(self):
        contexts = [self.__cause__ or self.__context__]
        while contexts[len(contexts) - 1]:
            last_context = contexts[len(contexts) - 1]
            contexts.append(last_context.__context__ or last_context.__cause__)
        return {
            "contexts": contexts,
        }

    def __setstate__(self, state):
        contexts = state["contexts"]
        self.__context__ = contexts[0]
        context = self.__context__
        for i in range(0, len(contexts) - 1):
            context.__context__ = contexts[i]

    def __reduce__(self):
        return (self.__class__, (self._request, self._response), self.__getstate__())

    def _concatenate(self, *strings):
        return self.MESSAGE_DELIMITER.join(filter(None, strings))


class HttpError(ServiceError):
    def __init__(self, request, response):
        super().__init__(request, response)


class HttpErrorTypecast:
    HTTP_BAD_REQUEST_CODE = 400

    @classmethod
    def is_bad_request_error(cls, http_error):
        return isinstance(http_error, Error) and http_error.response_code() == cls.HTTP_BAD_REQUEST_CODE


@contextmanager
def suppress_http_error(*statuses):
    """
    Suppress http error with specified status codes.

    :param statuses: list of status codes
    """
    try:
        yield
    except HttpError as e:
        if e.response.status_code in statuses:
            return None
        raise
