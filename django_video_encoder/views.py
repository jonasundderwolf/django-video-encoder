import logging

from django.conf import settings
from django.core import signing
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .tasks import get_video_task

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def notification(request):
    if getattr(settings, "ZENCODER_NOTIFICATION_SECRET", None) and (
        request.META.get("HTTP_X_ZENCODER_NOTIFICATION_SECRET")
        != settings.ZENCODER_NOTIFICATION_SECRET
    ):
        logger.warning(
            "Invalid Zencoder notification secret", extra={"request": request}
        )
        return HttpResponse("Invalid notification secret", status=400)  # BAD REQUEST

    try:
        data = signing.loads(request.META["QUERY_STRING"])
    except signing.BadSignature:
        logger.warning(
            "Invalid payload for Zencoder notification", extra={"request": request}
        )
        return HttpResponse("Invalid payload", status=400)  # BAD REQUEST

    get_video_task.delay(
        data["ct"], data["obj"], data["fld"], request.body.decode("utf-8")
    )
    return HttpResponse(status=204)  # NO CONTENT
