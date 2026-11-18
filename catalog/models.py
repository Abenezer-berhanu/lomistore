from django.conf import settings
from django.db import models


class Product(models.Model):
    """One channel post = one product. The photo stays on Telegram; we keep its file_id."""

    channel_message_id = models.PositiveBigIntegerField(unique=True, help_text="Post number in the channel")
    photo_file_id = models.CharField(max_length=255)
    name = models.CharField(max_length=200)
    price = models.PositiveIntegerField(help_text="Whole birr (ETB)")
    sizes = models.JSONField(default=list, help_text="Available sizes, e.g. [40, 41, 42]")
    description = models.TextField(blank=True)
    is_sold_out = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name

    @property
    def post_url(self) -> str:
        return f"https://t.me/{settings.TELEGRAM_CHANNEL_USERNAME}/{self.channel_message_id}"

    @property
    def order_url(self) -> str:
        # Deep link: opens the bot and sends "/start p<id>" automatically.
        return f"https://t.me/{settings.TELEGRAM_BOT_USERNAME}?start=p{self.channel_message_id}"

    @property
    def sizes_text(self) -> str:
        return ", ".join(str(size) for size in self.sizes)
