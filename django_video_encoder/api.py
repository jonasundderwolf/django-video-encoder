import datetime
import json
import logging
import os
from os.path import basename
from urllib.error import URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen, urlretrieve

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core import signing
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.http.multipartparser import parse_header
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


def _absolute_url(url):
    """
    Helper to turn a domain-relative URL into an absolute one
    with protocol and domain
    """
    if "://" in url:
        return url
    domain = Site.objects.get_current().domain
    protocol = (
        "https" if getattr(settings, "ZENCODER_NOTIFICATION_SSL", False) else "http"
    )
    base_url = f"{protocol}://{domain}"
    return urljoin(base_url, url)


def _get_encode_request_data(content_type_pk, field_name, file_url, obj_pk):
    color_metadata = "preserve"
    if getattr(settings, "ZENCODER_DISCARD_COLOR_METADATA", "preserve"):
        color_metadata = "discard"
    data = {
        "obj": obj_pk,
        "ct": content_type_pk,
        "fld": field_name,
    }
    notification_url = (
        f'{_absolute_url(reverse("zencoder_notification"))}?{signing.dumps(data)}'
    )
    outputs = []
    for label, format_dict in settings.DJANGO_VIDEO_ENCODER_FORMATS.items():
        output_dict = {
            "label": label,
            "notifications": [notification_url],
            "color_metadata": color_metadata,
        }
        output_dict.update(**format_dict)
        outputs.append(output_dict)
    data = {
        "input": _absolute_url(file_url),
        "region": getattr(settings, "ZENCODER_REGION", "europe"),
        "output": outputs,
        "test": getattr(settings, "ZENCODER_INTEGRATION_MODE", False),
    }
    # get thumbnails for first output only
    data["output"][0]["thumbnails"] = {
        "interval": settings.DJANGO_VIDEO_ENCODER_THUMBNAIL_INTERVAL,
        "start_at_first_frame": True,
        "format": "jpg",
    }
    return data


def encode(obj, field_name, file_url=None):

    if not file_url:
        file_url = getattr(obj, field_name).url
    content_type = ContentType.objects.get_for_model(type(obj))
    data = _get_encode_request_data(content_type.pk, field_name, file_url, obj.pk)

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
            "The object %s/%s has been removed after being sent to Zencoder",
            content_type,
            object_id,
        )
        return
    else:
        if output["state"] == "finished":

            from .models import Format, Thumbnail

            # get preview pictures
            if output.get("thumbnails"):
                for i, thumbnail in enumerate(output["thumbnails"][0]["images"]):
                    filename, __ = urlretrieve(thumbnail["url"])
                    thmb, __ = Thumbnail.objects.get_or_create(
                        content_type=content_type,
                        object_id=object_id,
                        time=i * settings.DJANGO_VIDEO_ENCODER_THUMBNAIL_INTERVAL,
                        width=output["width"],
                        height=output["height"],
                    )
                    thmb.image.save(basename(filename), File(open(filename, "rb")))
                    os.unlink(filename)

            fmt, __ = Format.objects.get_or_create(
                format_label=output["label"],
                content_type=content_type,
                object_id=object_id,
                field_name=field_name,
                video_codec=output["video_codec"],
                width=output["width"],
                height=output["height"],
                duration=output["duration_in_ms"],
            )

            response = open_url(output["url"])
            headers = response.info()
            try:
                # parse content-disposition header
                filename = parse_header(headers["Content-Disposition"])[1]["filename"]
            except (KeyError, TypeError):
                extension = headers["Content-Type"].rsplit("/", 1)[1]
                datetime_now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"format_{datetime_now}.{extension}"
            else:
                # remove trailing parameters
                filename = filename.split("?", 1)[0]

            f = File(response)
            fmt.width = output["width"]
            fmt.height = output["height"]
            fmt.duration = output["duration_in_ms"]
            fmt.extra_info = data
            fmt.file.save(basename(filename), f)
            logger.info("File %s saved as %s", filename, fmt.file.name)
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
