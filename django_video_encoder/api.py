import cgi
import datetime
import json
import logging
import os
from os.path import basename
from urllib.error import URLError
from urllib.request import Request, urlopen, urlretrieve

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core import signing
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.urls import reverse

from . import signals
from .errors import ZencoderError

logger = logging.getLogger(__name__)


def open_url(url, data=None):
    if data:
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
        }
        request = Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
    else:
        request = Request(url)

    try:
        response = urlopen(request)
    except URLError as e:
        raise ZencoderError(e.reason)

    if response.getcode() // 100 != 2:
        try:
            raise ZencoderError(", ".join(json.loads(response.text)["errors"]))
        except ValueError:
            raise ZencoderError(response.reason or "HTTP error: %d" % response.status)

    return response


def send_request(data):
    data["api_key"] = settings.ZENCODER_API_KEY
    response = open_url("https://app.zencoder.com/api/v2/jobs", data)
    return json.loads(response.read().decode("utf-8"))


def encode(obj, field_name, file_url=None):
    def absolute_url(url):
        """
        Helper to turn a domain-relative URL into an absolute one
        with protocol and domain
        """
        domain = Site.objects.get_current().domain
        protocol = (
            "https" if getattr(settings, "ZENCODER_NOTIFICATION_SSL", False) else "http"
        )
        return url if "://" in url else "%s://%s%s" % (protocol, domain, url)

    if not file_url:
        file_url = getattr(obj, field_name).url

    content_type = ContentType.objects.get_for_model(type(obj))

    color_metadata = "preserve"
    if getattr(settings, "ZENCODER_DISCARD_COLOR_METADATA", "preserve"):
        color_metadata = "discard"

    outputs = []
    for fmt in settings.DJANGO_VIDEO_ENCODER_FORMATS:
        data = {
            "obj": obj.pk,
            "ct": content_type.pk,
            "fld": field_name,
        }
        notification_url = "%s?%s" % (
            absolute_url(reverse("zencoder_notification")),
            signing.dumps(data),
        )

        outputs.append(
            {
                "label": fmt["label"],
                "video_codec": fmt["codec"],
                "width": fmt.get("width"),
                "height": fmt.get("height"),
                "notifications": [notification_url],
                "color_metadata": color_metadata,
            }
        )

    data = {
        "input": absolute_url(file_url),
        "region": getattr(settings, "ZENCODER_REGION", "europe"),
        "output": outputs,
        "test": getattr(settings, "ZENCODER_INTEGRATION_MODE", False),
    }

    # get thumbnails for first output only
    data["output"][0]["thumbnails"] = {
        "interval": settings.DJANGO_VIDEO_ENCODER_THUMBNAIL_INTERVAL,
        "start_at_first_frame": 1,
        "format": "jpg",
    }

    try:
        result = send_request(data)
    except ZencoderError as e:
        result = None
        logger.warning(
            "Error when sending encoding request to zencoder for %s/%s/%s: %s",
            content_type,
            obj.pk,
            field_name,
            e,
        )
        signals.sending_failed.send(sender=type(obj), instance=obj, error=e)
    else:
        logger.info(
            "Sent encoding request for %s/%s/%s, job id: %s",
            content_type,
            obj.pk,
            field_name,
            result["id"],
        )
        signals.sent_to_zencoder.send(sender=type(obj), instance=obj, result=result)
    return result


def get_video(content_type_id, object_id, field_name, data):
    content_type = ContentType.objects.get(id=content_type_id)
    logger.info("Getting video file for %s/%s/%s", content_type, object_id, field_name)

    output = json.loads(data)["output"]

    try:
        obj = content_type.get_object_for_this_type(pk=object_id)
    except ObjectDoesNotExist:
        logger.warning(
            "The model %s/%s has been removed after being sent to Zencoder",
            content_type,
            object_id,
            field_name,
        )
    else:
        if output["state"] == "finished":

            from .models import Format, Thumbnail

            # get preview pictures
            if output.get("thumbnails"):
                for i, thumbnail in enumerate(output["thumbnails"][0]["images"]):
                    filename, header = urlretrieve(thumbnail["url"])
                    thmb, __ = Thumbnail.objects.get_or_create(
                        content_type=content_type,
                        object_id=object_id,
                        time=i * settings.DJANGO_VIDEO_ENCODER_THUMBNAIL_INTERVAL,
                    )
                    thmb.image.save(basename(filename), File(open(filename, "rb")))
                    os.unlink(filename)

            fmt, __ = Format.objects.get_or_create(
                content_type=content_type,
                object_id=object_id,
                field_name=field_name,
                format=output["label"],
            )

            response = open_url(output["url"])
            try:
                # parse content-disposition header
                filename = cgi.parse_header(response.info()["Content-Disposition"])[1][
                    "filename"
                ]
            except (KeyError, TypeError):
                filename = "format_%s.%s" % (
                    datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),
                    response.info()["Content-Type"].rsplit("/", 1)[1],
                )

            # remove trailing parameters
            filename = filename.split("?", 1)[0]

            f = File(response)
            f.size = response.info()["Content-Length"]

            fmt.width = output["width"]
            fmt.height = output["height"]
            fmt.duration = output["duration_in_ms"]
            fmt.extra_info = data
            fmt.file.save(basename(filename), f)
            logger.info(u"File %s saved as %s", filename, fmt.file.name)
            signals.received_format.send(
                sender=type(obj), instance=obj, format=fmt, result=data
            )

        elif output["state"] == "failed":
            logger.warning(
                "Zencoder error for %s/%s/%s: %s",
                content_type,
                object_id,
                field_name,
                output["error_message"],
            )
            signals.encoding_failed.send(sender=type(obj), instance=obj, result=data)

        else:
            logger.error(
                "Unknown zencoder status for %s/%s/%s: %s",
                content_type,
                object_id,
                field_name,
                data,
            )
