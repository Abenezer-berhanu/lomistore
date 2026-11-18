from typing import Any

from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .live import GROUP


class OrdersConsumer(AsyncJsonWebsocketConsumer):
    """One open dashboard tab = one consumer. Staff only."""

    async def connect(self) -> None:
        user = self.scope.get("user")
        if user is None or not user.is_staff:
            # Accept, then close with our own code, so the page can show "logged out"
            # instead of retrying forever (a refused handshake looks like a network error).
            await self.accept()
            await self.close(code=4403)
            return
        await self.channel_layer.group_add(GROUP, self.channel_name)
        await self.accept()

    async def disconnect(self, code: int) -> None:
        await self.channel_layer.group_discard(GROUP, self.channel_name)

    # Called for group messages with {"type": "order.update"} (the dot becomes an underscore).
    async def order_update(self, event: dict[str, Any]) -> None:
        await self.send_json({"type": "order", "order": event["order"]})
