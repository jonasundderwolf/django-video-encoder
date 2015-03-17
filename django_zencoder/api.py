import os
from os.path import basename
import json
import logging
import urllib
import urllib2
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.core.files import File
from django.contrib.sites.models import Site
from django.conf import settings
from django.core import signing
from .errors import ZencoderError

logger = logging.getLogger(__name__)


def send_request(data):
    headers = {
        "Content-type": "application/json",
        "Accept": "application/json",
    }
    data['api_key'] = settings.ZENCODER_API_KEY
    request = urllib2.Request('https://app.zencoder.com/api/v2/jobs',
                              data=json.dumps(data), headers=headers)
    try:
        response = urllib2.urlopen(request)
    except urllib2.URLError, e:
        raise ZencoderError(e.reason)

    if response.getcode() // 100 != 2:
        try:
            raise ZencoderError(', '.join(json.loads(response.text)['errors']))
        except ValueError:
            raise ZencoderError(response.reason or 'HTTP error: %d' % response.status)
    return json.loads(response.read())


def encode(obj, field_name, file_url=None):

    def absolute_url(url):
        """
        Helper to turn a domain-relative URL into an absolute one
        with protocol and domain
        """
        domain = Site.objects.get_current().domain
        protocol = 'https' if getattr(
            settings, 'ZENCODER_NOTIFICATION_SSL', False) else 'http'
        return url if '://' in url else '%s://%s%s' % (protocol, domain, url)

    if not file_url:
        file_url = getattr(obj, field_name).url

    content_type = ContentType.objects.get_for_model(type(obj))
    outputs = []
    for fmt in settings.ZENCODER_FORMATS:
        data = {
            'obj': obj.pk,
            'ct': content_type.pk,
            'fld': field_name,
        }
        notification_url = '%s?%s' % (
            absolute_url(reverse('zencoder_notification')), signing.dumps(data))

        outputs.append({
            "video_codec": format,
            "label": fmt['label'],
            "video_codec": fmt['codec'],
            "width": fmt.get("width"),
            "height": fmt.get("height"),
            "notifications": [notification_url],
        })

    data = {
        "input": absolute_url(file_url),
        "region": getattr(settings, 'ZENCODER_REGION', "europe"),
        "output": outputs,
        "test": getattr(settings, 'ZENCODER_INTEGRATION_MODE', False),
    }
    try:
        result = send_request(data)
        logger.info('Sent encoding request for %s/%s/%s, job id: %s',
                    content_type, obj.pk, field_name, result['id'])
    except ZencoderError, e:
        result = None
        logger.warning('Error when sending encoding request to zencoder for %s/%s/%s: %s',
                       content_type, obj.pk, field_name, e)
    return result


def get_video(content_type_id, object_id, field_name, data):
    content_type = ContentType.objects.get(id=content_type_id)
    logger.info('Getting video file for %s/%s/%s', content_type, object_id, field_name)

    output = json.loads(data)['output']

    if output['state'] == 'finished':
        from .models import Format

        fmt, __ = Format.objects.get_or_create(
            content_type=content_type,
            object_id=object_id,
            field_name=field_name,
            format=output['label'])

        # TODO: confirm that the referenced object still exists, it might have been
        # deleted between the encoding request and the notification

        filename, header = urllib.urlretrieve(output['url'])
        fmt.width = output['width']
        fmt.height = output['height']
        fmt.duration = output['duration_in_ms']
        fmt.extra_info = data
        fmt.file.save(basename(filename), File(open(filename, 'r')))
        os.unlink(filename)

    elif output['state'] == 'failed':
        logger.warning('Error in format %s for video %s: %s',
                       fmt.id, fmt.content_type, fmt.object_id,
                       fmt.field_name, output['error_message'])
