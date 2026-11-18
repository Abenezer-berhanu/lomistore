"""A very small Telegram Bot API client. The API is just "POST JSON to /bot<token>/<method>"."""

from functools import cache
from typing import Any, Protocol

import httpx
from django.conf import settings


class TelegramError(Exception):
    def __init__(self, description: str, code: int | None = None) -> None:
        super().__init__(description)
        self.description = description
        self.code = code


class Bot(Protocol):
    """Anything with this call() works as a bot. Tests pass a fake that records calls."""

    def call(self, method: str, **params: Any) -> Any: ...


class TelegramClient:
    def __init__(self, token: str, timeout: float = 10.0) -> None:
        self._base_url = f"https://api.telegram.org/bot{token}/"
        self._http = httpx.Client(timeout=timeout)

    def call(self, method: str, **params: Any) -> Any:
        payload = {key: value for key, value in params.items() if value is not None}
        try:
            response = self._http.post(self._base_url + method, json=payload)
            data = response.json()
        except (httpx.HTTPError, ValueError) as err:
            # Don't include the URL: it contains the bot token.
            raise TelegramError(f"{method} failed: {type(err).__name__}") from None
        if not data.get("ok"):
            raise TelegramError(data.get("description", "Unknown error"), data.get("error_code"))
        return data["result"]


@cache
def get_client() -> TelegramClient:
    return TelegramClient(settings.TELEGRAM_BOT_TOKEN)
