import logging

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Format

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def notification(request, id):
    logger.info('Got zencoder notification for job %s', id)
    fmt = Format.objects.get(id=int(id))
    fmt.get_video(request.body)
    return HttpResponse(status=204)  # NO CONTENT
