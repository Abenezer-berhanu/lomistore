from django.contrib import admin
from django.utils.html import format_html

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "sizes_text", "is_sold_out", "channel_post", "created_at"]
    list_editable = ["is_sold_out"]
    list_filter = ["is_sold_out", "created_at"]
    search_fields = ["name", "description"]
    readonly_fields = ["channel_message_id", "photo_file_id", "channel_post", "created_at", "updated_at"]
    fields = [
        "name",
        "price",
        "sizes",
        "description",
        "is_sold_out",
        "channel_post",
        "channel_message_id",
        "photo_file_id",
        "created_at",
        "updated_at",
    ]

    @admin.display(description="Sizes")
    def sizes_text(self, product: Product) -> str:
        return product.sizes_text

    @admin.display(description="Channel post")
    def channel_post(self, product: Product) -> str:
        return format_html('<a href="{}" target="_blank" rel="noopener">Open post</a>', product.post_url)

    def has_add_permission(self, request) -> bool:
        # Products are created by posting in the channel, never by hand.
        return False
