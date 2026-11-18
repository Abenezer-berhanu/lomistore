"""Push order changes to every open dashboard over WebSockets."""

import logging
from typing import Any

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.urls import reverse
from django.utils import timezone

from .models import Order

logger = logging.getLogger(__name__)

GROUP = "orders"


def order_payload(order: Order) -> dict[str, Any]:
    """The JSON the dashboard uses to draw one row. Same shape for first load and live updates."""
    customer = order.customer
    return {
        "id": order.pk,
        "created_at": timezone.localtime(order.created_at).strftime("%b %d, %H:%M"),
        "product_name": order.product_name,
        "size": order.size,
        "price": order.price,
        "phone": order.phone,
        "phone_is_own": order.phone_is_own,
        "customer": customer.full_name or "No name",
        "username": customer.username,
        "status": order.status,
        "status_label": order.get_status_display(),
        "admin_url": reverse("admin:orders_order_change", args=[order.pk]),
    }


def broadcast_order(order: Order) -> None:
    layer = get_channel_layer()
    if layer is None:
        return
    try:
        async_to_sync(layer.group_send)(GROUP, {"type": "order.update", "order": order_payload(order)})
    except Exception:
        # A dashboard that misses one update is fine; a lost order is not. Never raise here.
        logger.exception("Could not broadcast order %s", order.pk)
