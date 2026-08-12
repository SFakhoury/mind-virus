from __future__ import annotations

from dataclasses import dataclass
import hmac
import os


@dataclass(frozen=True)
class APIAuthenticator:
    """Validate an app token without ever exposing the provider API key."""

    access_token: str | None = None

    @classmethod
    def from_environment(cls, *, required: bool = False) -> "APIAuthenticator":
        token = os.getenv("MIND_VIRUS_ACCESS_TOKEN")
        if required and not token:
            raise RuntimeError("MIND_VIRUS_ACCESS_TOKEN is required in production mode.")
        return cls(token)

    @property
    def enabled(self) -> bool:
        return self.access_token is not None

    def authorize(self, supplied_token: str | None) -> bool:
        if not self.enabled:
            return True
        return bool(supplied_token) and hmac.compare_digest(supplied_token, self.access_token)
