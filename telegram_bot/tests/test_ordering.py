import pytest

from conftest import CUSTOMER_ID, private_message, size_tap
from orders.models import Customer, Order
from telegram_bot.handlers import handle_update

STAFF_CHAT = -1001234567890


@pytest.fixture
def picked_size(product, bot):
    """Customer opened the product and tapped size 42."""
    handle_update(private_message("/start p45"), bot)
    handle_update(size_tap(f"size:{product.pk}:42"), bot)
    return product


def test_start_link_shows_product_with_size_buttons(product, bot) -> None:
    handle_update(private_message("/start p45"), bot)

    [photo] = bot.sent("sendPhoto")
    assert photo["photo"] == "photo-file-id"
    assert "3,500 ETB" in photo["caption"]
    buttons = [button["text"] for row in photo["reply_markup"]["inline_keyboard"] for button in row]
    assert buttons == ["40", "41", "42"]


def test_tapping_a_size_asks_for_phone(product, bot) -> None:
    handle_update(private_message("/start p45"), bot)
    handle_update(size_tap(f"size:{product.pk}:42"), bot)

    assert bot.sent("answerCallbackQuery")
    last = bot.sent("sendMessage")[-1]
    assert last["reply_markup"]["keyboard"][0][0]["request_contact"] is True
    customer = Customer.objects.get(telegram_id=CUSTOMER_ID)
    assert (customer.pending_product_id, customer.pending_size) == (product.pk, 42)


def test_sharing_own_contact_places_order_and_notifies_staff(picked_size, bot) -> None:
    contact = {"phone_number": "251911223344", "user_id": CUSTOMER_ID, "first_name": "Abebe"}

    handle_update(private_message(contact=contact), bot)

    order = Order.objects.get()
    assert (order.size, order.price, order.phone, order.phone_is_own) == (42, 3500, "+251911223344", True)
    assert order.status == Order.Status.NEW
    customer = Customer.objects.get(telegram_id=CUSTOMER_ID)
    assert customer.verified_phone == "+251911223344"
    assert customer.pending_product is None
    assert "order #" in bot.texts_to(CUSTOMER_ID)[-1].lower()
    [staff_message] = bot.texts_to(STAFF_CHAT)
    assert "+251911223344" in staff_message
    assert "not the customer's own" not in staff_message


def test_someone_elses_contact_is_accepted_but_marked(picked_size, bot) -> None:
    contact = {"phone_number": "+251911000000", "user_id": 999, "first_name": "Mom"}

    handle_update(private_message(contact=contact), bot)

    order = Order.objects.get()
    assert (order.phone, order.phone_is_own) == ("+251911000000", False)
    assert "not the customer's own" in bot.texts_to(STAFF_CHAT)[0]


def test_typed_phone_is_normalized_and_marked_unverified(picked_size, bot) -> None:
    handle_update(private_message("0922 33 44 55"), bot)

    order = Order.objects.get()
    assert (order.phone, order.phone_is_own) == ("+251922334455", False)


def test_invalid_typed_phone_asks_again(picked_size, bot) -> None:
    handle_update(private_message("hello"), bot)

    assert not Order.objects.exists()
    assert "doesn't look like a phone number" in bot.texts_to(CUSTOMER_ID)[-1]


def test_sold_out_product_cannot_be_ordered(product, bot) -> None:
    product.is_sold_out = True
    product.save()

    handle_update(private_message("/start p45"), bot)

    assert not bot.sent("sendPhoto")
    assert "sold out" in bot.texts_to(CUSTOMER_ID)[-1]


def test_size_that_is_not_offered_is_refused(product, bot) -> None:
    handle_update(size_tap(f"size:{product.pk}:47"), bot)

    assert "size 47 is no longer available" in bot.texts_to(CUSTOMER_ID)[-1]


def test_plain_start_sends_welcome(db, bot) -> None:
    handle_update(private_message("/start"), bot)

    assert "Welcome to Lomi Store" in bot.texts_to(CUSTOMER_ID)[0]


def test_chatid_command_replies_with_the_chat_id(db, bot) -> None:
    update = private_message("/chatid@lomistore_bot")
    update["message"]["chat"] = {"id": STAFF_CHAT, "type": "supergroup"}

    handle_update(update, bot)

    assert bot.texts_to(STAFF_CHAT) == [f"This chat id is {STAFF_CHAT}"]
