from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import Customer, Order


def _set_status(queryset: QuerySet[Order], status: str) -> None:
    # save() one by one (not queryset.update) so the live dashboard hears about each change.
    for order in queryset:
        order.status = status
        order.save(update_fields=["status", "updated_at"])


@admin.action(description="Mark as called")
def mark_called(modeladmin, request: HttpRequest, queryset: QuerySet[Order]) -> None:
    _set_status(queryset, Order.Status.CALLED)


@admin.action(description="Mark as confirmed")
def mark_confirmed(modeladmin, request: HttpRequest, queryset: QuerySet[Order]) -> None:
    _set_status(queryset, Order.Status.CONFIRMED)


@admin.action(description="Mark as delivered")
def mark_delivered(modeladmin, request: HttpRequest, queryset: QuerySet[Order]) -> None:
    _set_status(queryset, Order.Status.DELIVERED)


@admin.action(description="Mark as cancelled")
def mark_cancelled(modeladmin, request: HttpRequest, queryset: QuerySet[Order]) -> None:
    _set_status(queryset, Order.Status.CANCELLED)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at", "product_name", "size", "price", "phone", "phone_is_own", "customer", "status"]
    list_display_links = ["id", "product_name"]
    list_editable = ["status"]
    list_filter = ["status", "phone_is_own", "created_at"]
    search_fields = ["phone", "product_name", "customer__first_name", "customer__last_name", "customer__username"]
    list_select_related = ["customer"]
    date_hierarchy = "created_at"
    actions = [mark_called, mark_confirmed, mark_delivered, mark_cancelled]
    readonly_fields = [
        "customer",
        "product",
        "product_name",
        "price",
        "size",
        "phone",
        "phone_is_own",
        "created_at",
        "updated_at",
    ]
    fields = ["status", "note", *readonly_fields]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False  # orders only come from the bot


class OrderInline(admin.TabularInline):
    model = Order
    fields = ["id", "created_at", "product_name", "size", "price", "phone", "status"]
    readonly_fields = fields
    extra = 0
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request: HttpRequest, obj=None) -> bool:
        return False


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["telegram_id", "full_name", "username", "phone", "verified_phone", "created_at"]
    search_fields = ["first_name", "last_name", "username", "phone", "verified_phone"]
    readonly_fields = [
        "telegram_id",
        "first_name",
        "last_name",
        "username",
        "phone",
        "verified_phone",
        "pending_product",
        "pending_size",
        "created_at",
    ]
    inlines = [OrderInline]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
