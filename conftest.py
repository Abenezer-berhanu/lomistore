"""Shared pytest fixtures: a fake Telegram bot and builders for Telegram updates."""

from typing import Any

import pytest

from catalog.models import Product

CHANNEL_ID = -1009876543210
CUSTOMER_ID = 111222333


class FakeBot:
    """Records every API call instead of talking to Telegram."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.errors: dict[str, Exception] = {}

    def call(self, method: str, **params: Any) -> Any:
        self.calls.append((method, params))
        if method in self.errors:
            raise self.errors[method]
        return {"message_id": 1}

    def sent(self, method: str) -> list[dict[str, Any]]:
        return [params for name, params in self.calls if name == method]

    def texts_to(self, chat_id: int) -> list[str]:
        return [params["text"] for params in self.sent("sendMessage") if params["chat_id"] == chat_id]


@pytest.fixture
def bot() -> FakeBot:
    return FakeBot()


@pytest.fixture
def product(db) -> Product:
    return Product.objects.create(
        channel_message_id=45,
        photo_file_id="photo-file-id",
        name="Nike Air Force 1 White",
        price=3500,
        sizes=[40, 41, 42],
    )


def channel_post(message_id: int = 45, caption: str = "", **extra: Any) -> dict[str, Any]:
    post = {
        "message_id": message_id,
        "chat": {"id": CHANNEL_ID, "type": "channel", "username": "lomistore"},
        "photo": [{"file_id": "small"}, {"file_id": "large"}],
        "caption": caption,
    }
    post.update(extra)
    return {"update_id": 1, "channel_post": post}


def private_message(text: str | None = None, contact: dict | None = None, user_id: int = CUSTOMER_ID) -> dict[str, Any]:
    message: dict[str, Any] = {
        "message_id": 10,
        "chat": {"id": user_id, "type": "private"},
        "from": {"id": user_id, "first_name": "Abebe", "last_name": "Kebede", "username": "abebe"},
    }
    if text is not None:
        message["text"] = text
    if contact is not None:
        message["contact"] = contact
    return {"update_id": 2, "message": message}


def size_tap(data: str, user_id: int = CUSTOMER_ID) -> dict[str, Any]:
    return {
        "update_id": 3,
        "callback_query": {"id": "cb1", "data": data, "from": {"id": user_id, "first_name": "Abebe"}},
    }
