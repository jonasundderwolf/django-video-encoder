import os
from os.path import basename
import json
import logging
import urllib
import urllib2
from django.core.urlresolvers import reverse
from django.core.files import File
from django.contrib.sites.models import Site
from django.conf import settings
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
    from .models import Format
    def absolute_url(url):
        domain = Site.objects.get_current().domain
        domain = '694862d6.ngrok.com'
        return url if '://' in url else 'http://%s%s' % (domain, url)

    if not file_url:
        file_url = getattr(obj, field_name).url

    outputs = []
    for fmt in settings.ZENCODER_FORMATS:
        format = Format.objects.get_for(obj, field_name, fmt['label'], create=True)
        outputs.append({
            "video_codec": format,
            "label": fmt['label'],
            "video_codec": fmt['codec'],
            "width": fmt.get("width"),
            "height": fmt.get("height"),
            "notifications": [
                absolute_url(reverse('zencoder_notification', args=(format.id,)))],
        })

    data = {
        "input": absolute_url(file_url),
        "region": getattr(settings, 'ZENCODER_REGION', "europe"),
        "output": outputs,
    }
    try:
        result = send_request(data)
        logger.info('Sent zencoder encoding request for %s/%s/%s, job id: %s',
                    format.content_type, obj.pk, field_name, result['id'])
    except ZencoderError, e:
        result = None
        logger.warning('Error when sending encoding request to zencoder for %s/%s/%s: %s',
                       format.content_type, obj.pk, field_name, e)
    return result


def get_video(format, data):
    logger.info('Getting video file for %s/%s/%s, format id %s',
                format.content_type, format.object_id, format.field_name, format.id)

    output = json.loads(data)['output']
    if output['state'] == 'finished':
        filename, header = urllib.urlretrieve(output['url'])
        format.width = output['width']
        format.height = output['height']
        format.duration = output['duration_in_ms']
        format.extra_info = data
        format.file.save(basename(filename), File(open(filename, 'r')))
        os.unlink(filename)
    elif output['state'] == 'failed':
        logger.warning('Error in format %s for video %s: %s',
                       format.id, format.content_type, format.object_id, format.field_name,
                       output['error_message'])
