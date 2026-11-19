"""What the bot does with each Telegram update.

Flow:
  1. Staff post a photo + caption in the channel   -> product saved, Order button added
  2. Customer taps Order                           -> bot shows the product with size buttons
  3. Customer taps a size                          -> bot asks for a phone number
  4. Customer shares or types a phone              -> order saved, staff notified
"""

import logging
import re
from typing import Any

from django.conf import settings
from django.db import transaction
from django.urls import reverse

from catalog.caption import CaptionError, parse_caption
from catalog.models import Product
from orders.models import Customer, Order
from orders.phone import normalize_phone

from .client import Bot, TelegramError

logger = logging.getLogger(__name__)

Update = dict[str, Any]

START_PRODUCT = re.compile(r"^p(\d{1,18})$")
SIZE_CALLBACK = re.compile(r"^size:(\d{1,18}):(\d{1,3})$")
PHONE_EXAMPLE = "0911223344"


def handle_update(update: Update, bot: Bot) -> None:
    if post := update.get("channel_post") or update.get("edited_channel_post"):
        handle_channel_post(post, bot)
    elif message := update.get("message"):
        handle_message(message, bot)
    elif query := update.get("callback_query"):
        handle_callback(query, bot)


# 1. Channel posts --------------------------------------------------------------------------


def handle_channel_post(post: Update, bot: Bot) -> None:
    username = (post["chat"].get("username") or "").lower()
    if username != settings.TELEGRAM_CHANNEL_USERNAME.lower():
        return  # some other channel the bot was added to

    caption = post.get("caption") or ""
    photos = post.get("photo")
    if not photos or not caption:
        return  # text-only posts and album photos without a caption aren't products

    message_id = post["message_id"]
    try:
        parsed = parse_caption(caption)
    except CaptionError as error:
        # Only complain when staff clearly meant a product, not for announcements.
        if re.search(r"\b(price|sizes?)\s*:", caption, re.IGNORECASE):
            notify_staff(bot, f"Post {_post_url(message_id)} was not added.\nReason: {error}\nEdit the caption to fix it.")
        return

    product, created = Product.objects.update_or_create(
        channel_message_id=message_id,
        defaults={
            "photo_file_id": photos[-1]["file_id"],  # the last one is the largest size
            "name": parsed.name,
            "price": parsed.price,
            "sizes": list(parsed.sizes),
            "description": parsed.description,
            "is_sold_out": parsed.sold_out,
        },
    )
    logger.info("%s product %s from post %s", "Created" if created else "Updated", product.pk, message_id)

    if not post.get("reply_markup"):
        _add_order_button(bot, post["chat"]["id"], product)


def _add_order_button(bot: Bot, chat_id: int, product: Product) -> None:
    try:
        bot.call(
            "editMessageReplyMarkup",
            chat_id=chat_id,
            message_id=product.channel_message_id,
            reply_markup={"inline_keyboard": [[{"text": "Order now", "url": product.order_url}]]},
        )
    except TelegramError as error:
        if "not modified" in error.description:
            return
        notify_staff(
            bot,
            f"Saved {product.name}, but could not add the Order button to {product.post_url}.\n"
            f"Telegram said: {error.description}\n"
            "Check that the bot is a channel admin with 'Edit messages of others'. "
            "Albums (several photos in one post) can't have buttons: post one photo.",
        )


# 2 to 4. Private chat with customers ------------------------------------------------------


def handle_message(message: Update, bot: Bot) -> None:
    chat = message["chat"]
    text = (message.get("text") or "").strip()

    # Lets you find the admin group's id: send /chatid inside the group.
    if text.startswith("/chatid"):
        bot.call("sendMessage", chat_id=chat["id"], text=f"This chat id is {chat['id']}")
        return
    if chat["type"] != "private" or "from" not in message:
        return

    customer = _get_customer(message["from"])

    if text.startswith("/start"):
        payload = text.removeprefix("/start").strip()
        if match := START_PRODUCT.match(payload):
            show_product(bot, customer, int(match.group(1)))
        else:
            send_welcome(bot, customer)
    elif contact := message.get("contact"):
        handle_contact(bot, customer, message["from"]["id"], contact)
    elif text and customer.pending_product_id and customer.pending_size:
        handle_typed_phone(bot, customer, text)
    elif text and customer.pending_product_id:
        _send(bot, customer, "Please tap your size on the buttons above.")
    else:
        send_welcome(bot, customer)


def handle_callback(query: Update, bot: Bot) -> None:
    # Always answer, otherwise the button keeps showing a loading spinner.
    bot.call("answerCallbackQuery", callback_query_id=query["id"])

    match = SIZE_CALLBACK.match(query.get("data") or "")
    if not match:
        return
    customer = _get_customer(query["from"])
    product_id, size = int(match.group(1)), int(match.group(2))

    product = Product.objects.filter(pk=product_id).first()
    if product is None or product.is_sold_out:
        _send(bot, customer, "Sorry, this item is no longer available.")
        return
    if size not in product.sizes:
        _send(bot, customer, f"Sorry, size {size} is no longer available. Please choose another size.")
        return

    customer.pending_product = product
    customer.pending_size = size
    customer.save(update_fields=["pending_product", "pending_size"])
    ask_for_phone(bot, customer, product, size)


def send_welcome(bot: Bot, customer: Customer) -> None:
    channel = settings.TELEGRAM_CHANNEL_USERNAME
    _send(
        bot,
        customer,
        "Welcome to Lomi Store!\n\nBrowse our items in the channel and tap \"Order now\" under the one you like.",
        reply_markup={"inline_keyboard": [[{"text": "Open the channel", "url": f"https://t.me/{channel}"}]]},
    )


def show_product(bot: Bot, customer: Customer, channel_message_id: int) -> None:
    product = Product.objects.filter(channel_message_id=channel_message_id).first()
    if product is None:
        _send(bot, customer, "Sorry, this item is no longer available.")
        return
    if product.is_sold_out:
        _send(bot, customer, f"Sorry, {product.name} is sold out.")
        return

    customer.pending_product = product
    customer.pending_size = None
    customer.save(update_fields=["pending_product", "pending_size"])

    buttons = [{"text": str(size), "callback_data": f"size:{product.pk}:{size}"} for size in product.sizes]
    rows = [buttons[i : i + 4] for i in range(0, len(buttons), 4)]
    bot.call(
        "sendPhoto",
        chat_id=customer.telegram_id,
        photo=product.photo_file_id,
        caption=f"{product.name}\nPrice: {product.price:,} ETB\n\nChoose your size:",
        reply_markup={"inline_keyboard": rows},
    )


def ask_for_phone(bot: Bot, customer: Customer, product: Product, size: int) -> None:
    keyboard = [[{"text": "Share my phone number", "request_contact": True}]]
    if customer.phone:
        keyboard.append([{"text": customer.phone}])
    _send(
        bot,
        customer,
        f"{product.name}, size {size}.\n\n"
        f"Now send the phone number we should call. Tap the button below, or type it (example: {PHONE_EXAMPLE}).",
        reply_markup={"keyboard": keyboard, "resize_keyboard": True, "one_time_keyboard": True},
    )


def handle_contact(bot: Bot, customer: Customer, sender_id: int, contact: Update) -> None:
    raw = contact.get("phone_number", "")
    phone = normalize_phone(raw) or "+" + re.sub(r"\D", "", raw)
    # A contact card can belong to anyone. We accept it either way, but mark whose it is.
    is_own = contact.get("user_id") == sender_id
    if is_own and customer.verified_phone != phone:
        customer.verified_phone = phone
        customer.save(update_fields=["verified_phone"])

    if not (customer.pending_product_id and customer.pending_size):
        _send(bot, customer, "Thanks! Tap \"Order now\" under any item in our channel to order.", remove_keyboard=True)
        return
    place_order(bot, customer, phone, is_own)


def handle_typed_phone(bot: Bot, customer: Customer, text: str) -> None:
    phone = normalize_phone(text)
    if phone is None:
        _send(bot, customer, f"That doesn't look like a phone number. Please type it like {PHONE_EXAMPLE}.")
        return
    place_order(bot, customer, phone, is_own=phone == customer.verified_phone)


def place_order(bot: Bot, customer: Customer, phone: str, is_own: bool) -> None:
    with transaction.atomic():
        # Lock the customer row so two quick messages can't create the same order twice.
        # No select_related here: PostgreSQL can't lock the nullable side of an outer join.
        customer = Customer.objects.select_for_update().get(pk=customer.pk)
        product, size = customer.pending_product, customer.pending_size
        if product is None or size is None:
            return
        if product.is_sold_out:
            customer.pending_product, customer.pending_size = None, None
            customer.save(update_fields=["pending_product", "pending_size"])
            _send(bot, customer, f"Sorry, {product.name} just sold out.", remove_keyboard=True)
            return

        order = Order.objects.create(
            customer=customer,
            product=product,
            product_name=product.name,
            price=product.price,
            size=size,
            phone=phone,
            phone_is_own=is_own,
        )
        customer.phone = phone
        customer.pending_product, customer.pending_size = None, None
        customer.save(update_fields=["phone", "pending_product", "pending_size"])

    _send(
        bot,
        customer,
        f"Thank you! Your order #{order.pk} is received.\n\n"
        f"{order.product_name}\nSize: {order.size}\nPrice: {order.price:,} ETB\n\n"
        f"Lomi Store will call you at {order.phone} soon.",
        remove_keyboard=True,
    )
    notify_new_order(bot, order, product)


# Staff notifications ----------------------------------------------------------------------


def notify_new_order(bot: Bot, order: Order, product: Product) -> None:
    customer = order.customer
    who = customer.full_name or "No name"
    if customer.username:
        who += f" (@{customer.username})"
    phone_line = order.phone if order.phone_is_own else f"{order.phone}  (not the customer's own Telegram number)"
    admin_url = settings.PUBLIC_BASE_URL + reverse("admin:orders_order_change", args=[order.pk])
    notify_staff(
        bot,
        f"New order #{order.pk}\n\n"
        f"{order.product_name}\nSize: {order.size}\nPrice: {order.price:,} ETB\n\n"
        f"Phone: {phone_line}\nCustomer: {who}\n\n"
        f"Post: {product.post_url}\nOpen: {admin_url}",
    )


def notify_staff(bot: Bot, text: str) -> None:
    chat_id = settings.TELEGRAM_ADMIN_CHAT_ID
    if not chat_id:
        logger.warning("TELEGRAM_ADMIN_CHAT_ID is not set. Staff message not sent: %s", text)
        return
    try:
        bot.call("sendMessage", chat_id=chat_id, text=text, link_preview_options={"is_disabled": True})
    except TelegramError:
        logger.exception("Could not notify staff")


# Helpers ------------------------------------------------------------------------------------


def _get_customer(user: Update) -> Customer:
    customer, _ = Customer.objects.update_or_create(
        telegram_id=user["id"],
        defaults={
            "first_name": user.get("first_name", "")[:128],
            "last_name": user.get("last_name", "")[:128],
            "username": user.get("username", "")[:64],
        },
    )
    return customer


def _send(bot: Bot, customer: Customer, text: str, reply_markup: Update | None = None, remove_keyboard: bool = False) -> None:
    if remove_keyboard:
        reply_markup = {"remove_keyboard": True}
    bot.call("sendMessage", chat_id=customer.telegram_id, text=text, reply_markup=reply_markup)


def _post_url(message_id: int) -> str:
    return f"https://t.me/{settings.TELEGRAM_CHANNEL_USERNAME}/{message_id}"
