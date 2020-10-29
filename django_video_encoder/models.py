import os.path

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from django.utils.text import slugify

from .api import encode

VIDEO_ENCODER_MODELS = {}


def format_upload_to(instance, filename):
    dirname, original_filename = os.path.split(
        getattr(instance.video, instance.field_name).name
    )
    original_filename = slugify(os.path.splitext(original_filename)[0])
    extension = os.path.splitext(filename)[1].lower()
    return os.path.join(
        "formats",
        instance.format_label,
        dirname,
        f"{original_filename}{extension}",
    )


class Format(models.Model):
    H264 = "h264"
    HEVC = "hevc"
    JP2 = "jp2"
    MPEG4 = "mpeg4"
    THEORA = "theora"
    VP6 = "vp6"
    VP8 = "vp8"
    VP9 = "vp9"
    WMV = "wmv"
    VIDEO_CODEC_CHOICES = [
        (H264, H264),
        (HEVC, HEVC),
        (JP2, JP2),
        (MPEG4, MPEG4),
        (THEORA, THEORA),
        (VP6, VP6),
        (VP8, VP8),
        (VP9, VP9),
        (WMV, WMV),
    ]

    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    video = GenericForeignKey()
    field_name = models.CharField(max_length=255)

    format_label = models.CharField(max_length=80, editable=False, default="")
    video_codec = models.CharField(
        max_length=50, choices=VIDEO_CODEC_CHOICES, default=H264
    )
    file = models.FileField(upload_to=format_upload_to, max_length=2048)
    width = models.PositiveIntegerField("Width", null=True)
    height = models.PositiveIntegerField("Height", null=True)
    duration = models.PositiveIntegerField("Duration (ms)", null=True)

    extra_info = models.TextField("Encoder information (JSON)", blank=True)


def thumbnail_upload_to(instance, filename):
    return os.path.join(
        "footage", "thumbnails", str(instance.video.pk), f"{instance.time}.jpg"
    )


class Thumbnail(models.Model):
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    time = models.PositiveIntegerField("Time (s)")
    width = models.PositiveIntegerField("Width", null=True)
    height = models.PositiveIntegerField("Height", null=True)
    image = models.ImageField(
        upload_to=thumbnail_upload_to, max_length=512, blank=True, null=True
    )

    video = GenericForeignKey()


def detect_file_changes(sender, instance, **kwargs):
    field_name = VIDEO_ENCODER_MODELS.get(
        f"{sender._meta.app_label}.{sender._meta.model_name}"
    )
    if field_name:
        field = getattr(instance, field_name)
        if field and hasattr(field, "file") and isinstance(field.file, UploadedFile):
            if hasattr(instance, "_video_encoder_updates"):
                instance._video_encoder_updates.append(field_name)
            else:
                instance._video_encoder_updates = [field_name]


def trigger_encoding(sender, instance, **kwargs):
    for field in getattr(instance, "_video_encoder_updates", ()):
        encode(instance, field)


if getattr(settings, "VIDEO_ENCODER_MODELS", None):
    for name in settings.VIDEO_ENCODER_MODELS:
        app_model, field = name.rsplit(".", 1)
        VIDEO_ENCODER_MODELS[app_model.lower()] = field
    models.signals.pre_save.connect(detect_file_changes)
    models.signals.post_save.connect(trigger_encoding)
