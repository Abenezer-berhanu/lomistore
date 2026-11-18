from django.db import models


class ProcessedUpdate(models.Model):
    """Telegram resends an update when we answer slowly. Remembering ids stops double orders."""

    update_id = models.BigIntegerField(primary_key=True)
    received_at = models.DateTimeField(auto_now_add=True)
