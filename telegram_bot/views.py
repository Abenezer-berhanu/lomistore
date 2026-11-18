import json
import logging

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.utils.crypto import constant_time_compare
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .client import get_client
from .handlers import handle_update
from .models import ProcessedUpdate

logger = logging.getLogger(__name__)


@csrf_exempt  # Telegram can't send a CSRF token; the secret header below protects this URL instead
@require_POST
def webhook(request: HttpRequest) -> HttpResponse:
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    expected = settings.TELEGRAM_WEBHOOK_SECRET
    if not expected or not constant_time_compare(secret, expected):
        return HttpResponseForbidden()

    try:
        update = json.loads(request.body)
    except ValueError:
        return HttpResponseBadRequest()
    update_id = update.get("update_id") if isinstance(update, dict) else None
    if not isinstance(update_id, int):
        return HttpResponseBadRequest()

    _, is_new = ProcessedUpdate.objects.get_or_create(update_id=update_id)
    if not is_new:
        return HttpResponse("duplicate")

    try:
        handle_update(update, get_client())
    except Exception:
        # Answer 200 anyway. An error answer makes Telegram resend the same update again and again.
        logger.exception("Failed to handle update %s", update_id)
    return HttpResponse("ok")
