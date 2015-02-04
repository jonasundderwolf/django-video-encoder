import logging
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Format

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def notification(request, id):
    if getattr(settings, 'ZENCODER_NOTIFICATION_SECRET', None) and (
            request.META.get('HTTP_X_ZENCODER_NOTIFICATION_SECRET') !=
            settings.ZENCODER_NOTIFICATION_SECRET):
        logger.warn('Invalid notification secret for job %s', id)
        return HttpResponse('Invalid notification secret', status=400)  # BAD REQUEST

    logger.info('Got zencoder notification for job %s', id)
    fmt = Format.objects.get(id=int(id))
    fmt.get_video(request.body)
    return HttpResponse(status=204)  # NO CONTENT
