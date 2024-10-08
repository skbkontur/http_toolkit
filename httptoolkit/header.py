from base64 import b64encode
from dataclasses import dataclass
from typing import Callable, Iterable, Optional, Set


class KnownSensitiveHeaders:
    def __init__(self, items: Iterable[str] = []) -> None:
        self.items: Set[str] = set()
        self.update(items)

    def add(self, item: str) -> "KnownSensitiveHeaders":
        return self.update([item])

    def update(self, items: Iterable[str]) -> "KnownSensitiveHeaders":
        self.items.update(map(str.casefold, items))
        return self

    def __contains__(self, item: str) -> bool:
        return item.casefold() in self.items


known_sensitive_headers = KnownSensitiveHeaders(["Authorization"])


@dataclass(frozen=True)
class Header:
    """
    Custom HTTP-header.
    """

    name: str
    value: str
    is_sensitive: bool
    create_mask: Optional[Callable[[str], str]] = None

    """Use True, if the header value contains sensitive data. Sensitive headers will not be
    logged"""

    def __post_init__(self):
        if not (self.is_sensitive or self.name in known_sensitive_headers) and self.create_mask:
            raise RuntimeError(
                "'.mask' may only be set if is_sensitive = True\nor name is in KNOWN_SENSITIVE_HEADERS_NAMES"
            )

    def __str__(self) -> str:
        return f"{self.name}: {self.filtered_value}"

    @property
    def filtered_value(self) -> str:
        if self.is_sensitive or self.name in known_sensitive_headers:
            if self.create_mask is not None:
                return self.create_mask(self.value)
            return "[filtered]"
        return self.value


@dataclass(frozen=True)
class AuthSidHeader(Header):
    def __init__(self, value: str, create_mask: Optional[Callable[[str], str]] = None) -> None:
        super().__init__(
            name="Authorization",
            value=f"auth.sid {value}",
            is_sensitive=True,
            create_mask=create_mask,
        )


@dataclass(frozen=True)
class BearerAuthHeader(Header):
    def __init__(self, value: str, create_mask: Optional[Callable[[str], str]] = None) -> None:
        super().__init__(
            name="Authorization",
            value=f"Bearer {value}",
            is_sensitive=True,
            create_mask=create_mask,
        )


@dataclass(frozen=True)
class BasicAuthHeader(Header):
    def __init__(self, username: str, password: str, create_mask: Optional[Callable[[str], str]] = None) -> None:
        credentials = b64encode(f"{username}:{password}".encode("utf-8")).decode("utf-8")
        super().__init__(
            name="Authorization",
            value=f"Basic {credentials}",
            is_sensitive=True,
            create_mask=create_mask,
        )
