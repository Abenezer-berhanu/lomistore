from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .live import broadcast_order
from .models import Order


@receiver(post_save, sender=Order)
def push_order_to_dashboards(sender, instance: Order, **kwargs) -> None:
    # Wait for the database commit, so dashboards never show an order that was rolled back.
    transaction.on_commit(lambda: broadcast_order(instance))
