from django.apps import AppConfig


class OrdersConfig(AppConfig):
    name = "orders"
    verbose_name = "Orders"

    def ready(self) -> None:
        from . import signals  # noqa: F401  (connects the live-dashboard signal)
