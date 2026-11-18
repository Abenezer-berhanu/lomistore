"""Connect the bot to this server and check the channel setup.

Run once after deploying, and again whenever the domain or webhook secret changes:
    python manage.py telegram_setup
"""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.urls import reverse

from telegram_bot.client import TelegramError, get_client

ALLOWED_UPDATES = ["message", "callback_query", "channel_post", "edited_channel_post"]


class Command(BaseCommand):
    help = "Register the Telegram webhook and check that the bot can manage the channel."

    def handle(self, *args, **options) -> None:
        for name in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_WEBHOOK_SECRET", "TELEGRAM_CHANNEL_USERNAME", "TELEGRAM_BOT_USERNAME"):
            if not getattr(settings, name):
                raise CommandError(f"{name} is empty. Set it in .env and restart.")
        if not settings.PUBLIC_BASE_URL.startswith("https://"):
            raise CommandError("PUBLIC_BASE_URL must start with https:// (Telegram only calls HTTPS webhooks).")

        bot = get_client()
        try:
            me = bot.call("getMe")
            self.ok(f"Bot found: @{me['username']}")
            if me["username"].lower() != settings.TELEGRAM_BOT_USERNAME.lower():
                self.warn(f"TELEGRAM_BOT_USERNAME is '{settings.TELEGRAM_BOT_USERNAME}' but the token belongs to @{me['username']}")

            url = settings.PUBLIC_BASE_URL + reverse("telegram_bot:webhook")
            bot.call(
                "setWebhook",
                url=url,
                secret_token=settings.TELEGRAM_WEBHOOK_SECRET,
                allowed_updates=ALLOWED_UPDATES,
                max_connections=10,
            )
            self.ok(f"Webhook set to {url}")

            bot.call("setMyCommands", commands=[{"command": "start", "description": "Start ordering"}])

            self.check_channel(bot, me["id"])
            self.check_admin_group()

            info = bot.call("getWebhookInfo")
            if info.get("last_error_message"):
                self.warn(f"Telegram's last webhook error: {info['last_error_message']}")
        except TelegramError as error:
            raise CommandError(f"Telegram said: {error.description}") from None

    def check_channel(self, bot, bot_id: int) -> None:
        channel = "@" + settings.TELEGRAM_CHANNEL_USERNAME
        try:
            member = bot.call("getChatMember", chat_id=channel, user_id=bot_id)
        except TelegramError as error:
            self.warn(f"Can't see {channel}: {error.description}. Is the username right and the bot added as admin?")
            return
        if member.get("status") != "administrator":
            self.warn(f"The bot is not an admin of {channel}. Add it as admin.")
        elif not member.get("can_edit_messages"):
            self.warn(f"The bot is admin of {channel} but can't edit messages. Turn on 'Edit messages of others'.")
        else:
            self.ok(f"The bot is an admin of {channel} and can add Order buttons")

    def check_admin_group(self) -> None:
        if settings.TELEGRAM_ADMIN_CHAT_ID:
            self.ok(f"Staff notifications go to chat {settings.TELEGRAM_ADMIN_CHAT_ID}")
        else:
            self.warn("TELEGRAM_ADMIN_CHAT_ID is empty: staff won't get order messages. Send /chatid in the staff group.")

    def ok(self, text: str) -> None:
        self.stdout.write(self.style.SUCCESS(f"OK    {text}"))

    def warn(self, text: str) -> None:
        self.stdout.write(self.style.WARNING(f"CHECK {text}"))
