import json

import pytest

from conftest import FakeBot, private_message

URL = "/telegram/webhook/"


@pytest.fixture
def fake_bot(monkeypatch) -> FakeBot:
    fake = FakeBot()
    monkeypatch.setattr("telegram_bot.views.get_client", lambda: fake)
    return fake


def post(client, update: dict, secret: str = "test-secret"):
    return client.post(
        URL,
        data=json.dumps(update),
        content_type="application/json",
        headers={"X-Telegram-Bot-Api-Secret-Token": secret},
    )


def test_wrong_secret_is_rejected(db, client, fake_bot) -> None:
    response = post(client, private_message("/start"), secret="wrong")

    assert response.status_code == 403
    assert fake_bot.calls == []


def test_valid_update_is_handled_once(db, client, fake_bot) -> None:
    first = post(client, private_message("/start"))
    second = post(client, private_message("/start"))  # Telegram retrying the same update_id

    assert (first.status_code, first.content) == (200, b"ok")
    assert (second.status_code, second.content) == (200, b"duplicate")
    assert len(fake_bot.sent("sendMessage")) == 1


def test_errors_still_answer_200_so_telegram_does_not_retry(db, client, monkeypatch) -> None:
    def explode(update, bot):
        raise RuntimeError("boom")

    monkeypatch.setattr("telegram_bot.views.handle_update", explode)
    monkeypatch.setattr("telegram_bot.views.get_client", FakeBot)

    assert post(client, private_message("/start")).status_code == 200


def test_get_is_not_allowed(client) -> None:
    assert client.get(URL).status_code == 405
