from django.db import models

from catalog.models import Product


class Customer(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    first_name = models.CharField(max_length=128, blank=True)
    last_name = models.CharField(max_length=128, blank=True)
    username = models.CharField(max_length=64, blank=True)
    phone = models.CharField(max_length=20, blank=True, help_text="Last phone used for an order")
    verified_phone = models.CharField(
        max_length=20, blank=True, help_text="Phone of the customer's own Telegram account"
    )
    # The order in progress: product picked, then size, then phone.
    pending_product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    pending_size = models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.full_name or f"Telegram user {self.telegram_id}"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


class Order(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        CALLED = "called", "Called"
        CONFIRMED = "confirmed", "Confirmed"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="orders")
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL, related_name="orders")
    # Copies taken when the order is placed, so later edits to the product don't change old orders.
    product_name = models.CharField(max_length=200)
    price = models.PositiveIntegerField(help_text="Whole birr (ETB) at the time of the order")
    size = models.PositiveSmallIntegerField()
    phone = models.CharField(max_length=20)
    phone_is_own = models.BooleanField(help_text="Phone matches the customer's own Telegram account")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.NEW)
    note = models.TextField(blank=True, help_text="Staff notes, e.g. delivery address")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status", "-created_at"])]

    def __str__(self) -> str:
        return f"Order #{self.pk}"
