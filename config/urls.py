from django.contrib import admin
from django.http import HttpRequest, HttpResponse
from django.urls import include, path
from django.views.generic import RedirectView

admin.site.site_header = "Lomi Store admin"
admin.site.site_title = "Lomi Store"
admin.site.index_title = "Orders and products"
admin.site.site_url = "/dashboard/"  # the "View site" link opens the live dashboard


def health(request: HttpRequest) -> HttpResponse:
    return HttpResponse("ok")


urlpatterns = [
    path("", RedirectView.as_view(url="/dashboard/", permanent=False)),
    path("admin/", admin.site.urls),
    path("health/", health),
    path("telegram/", include("telegram_bot.urls")),
    path("", include("orders.urls")),
]
