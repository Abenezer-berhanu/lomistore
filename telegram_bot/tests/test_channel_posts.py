from catalog.models import Product
from conftest import channel_post
from telegram_bot.client import TelegramError
from telegram_bot.handlers import handle_update

CAPTION = "Nike Air Force 1 White\nPrice: 3,500 ETB\nSizes: 40-42\nOriginal"
STAFF_CHAT = -1001234567890


def test_new_post_creates_product_and_adds_order_button(db, bot) -> None:
    handle_update(channel_post(caption=CAPTION), bot)

    product = Product.objects.get(channel_message_id=45)
    assert (product.name, product.price, product.sizes) == ("Nike Air Force 1 White", 3500, [40, 41, 42])
    assert product.photo_file_id == "large"
    [edit] = bot.sent("editMessageReplyMarkup")
    assert edit["reply_markup"]["inline_keyboard"][0][0]["url"] == "https://t.me/lomistore_bot?start=p45"


def test_edited_post_updates_product_and_keeps_existing_button(db, bot) -> None:
    handle_update(channel_post(caption=CAPTION), bot)
    edited = channel_post(caption=CAPTION.replace("3,500", "3,200") + "\nSOLD OUT", reply_markup={"inline_keyboard": []})
    edited["edited_channel_post"] = edited.pop("channel_post")

    handle_update(edited, bot)

    product = Product.objects.get(channel_message_id=45)
    assert (product.price, product.is_sold_out) == (3200, True)
    assert len(bot.sent("editMessageReplyMarkup")) == 1  # only from the first post


def test_post_in_another_channel_is_ignored(db, bot) -> None:
    update = channel_post(caption=CAPTION)
    update["channel_post"]["chat"]["username"] = "someone_else"

    handle_update(update, bot)

    assert not Product.objects.exists()
    assert bot.calls == []


def test_bad_product_caption_tells_staff_why(db, bot) -> None:
    handle_update(channel_post(caption="Nike Air Max\nPrice: free\nSizes: 42"), bot)

    assert not Product.objects.exists()
    [message] = bot.texts_to(STAFF_CHAT)
    assert "Can't read price" in message
    assert "https://t.me/lomistore/45" in message


def test_announcement_photo_is_ignored_quietly(db, bot) -> None:
    handle_update(channel_post(caption="Happy holidays from Lomi Store!"), bot)

    assert not Product.objects.exists()
    assert bot.calls == []


def test_button_failure_is_reported_to_staff(db, bot) -> None:
    bot.errors["editMessageReplyMarkup"] = TelegramError("Bad Request: message can't be edited", 400)

    handle_update(channel_post(caption=CAPTION), bot)

    assert Product.objects.exists()
    [message] = bot.texts_to(STAFF_CHAT)
    assert "could not add the Order button" in message
