from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .live import order_payload
from .models import Order


@staff_member_required
def dashboard(request: HttpRequest) -> HttpResponse:
    orders = Order.objects.select_related("customer")[:50]
    return render(
        request,
        "orders/dashboard.html",
        {
            "orders": [order_payload(order) for order in orders],
            "new_count": Order.objects.filter(status=Order.Status.NEW).count(),
        },
    )
