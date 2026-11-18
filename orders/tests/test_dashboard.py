from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import AnonymousUser

from orders.consumers import OrdersConsumer
from orders.live import order_payload
from orders.models import Customer, Order


def make_order(product) -> Order:
    customer = Customer.objects.create(telegram_id=1, first_name="Abebe", username="abebe")
    return Order.objects.create(
        customer=customer,
        product=product,
        product_name=product.name,
        price=product.price,
        size=42,
        phone="+251911223344",
        phone_is_own=True,
    )


def test_dashboard_needs_staff_login(client) -> None:
    response = client.get("/dashboard/")

    assert response.status_code == 302
    assert "/admin/login/" in response["Location"]


def test_dashboard_lists_orders_for_staff(admin_client, product) -> None:
    make_order(product)

    response = admin_client.get("/dashboard/")

    assert response.status_code == 200
    assert b"Nike Air Force 1 White" in response.content


def test_saving_an_order_broadcasts_after_commit(product, django_capture_on_commit_callbacks, monkeypatch) -> None:
    sent = []
    monkeypatch.setattr("orders.signals.broadcast_order", sent.append)

    with django_capture_on_commit_callbacks(execute=True):
        order = make_order(product)

    assert sent == [order]


def test_staff_socket_receives_live_orders(admin_user, product) -> None:
    payload = order_payload(make_order(product))

    async def scenario():
        socket = WebsocketCommunicator(OrdersConsumer.as_asgi(), "/ws/orders/")
        socket.scope["user"] = admin_user
        connected, _ = await socket.connect()
        assert connected
        await get_channel_layer().group_send("orders", {"type": "order.update", "order": payload})
        assert await socket.receive_json_from() == {"type": "order", "order": payload}
        await socket.disconnect()

    async_to_sync(scenario)()


def test_anonymous_socket_is_closed() -> None:
    async def scenario():
        socket = WebsocketCommunicator(OrdersConsumer.as_asgi(), "/ws/orders/")
        socket.scope["user"] = AnonymousUser()
        await socket.connect()
        assert await socket.receive_output() == {"type": "websocket.close", "code": 4403}

    async_to_sync(scenario)()
