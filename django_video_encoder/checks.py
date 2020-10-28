from django.conf import settings
from django.core import checks

from django_video_encoder.models import Format


@checks.register
def check__formats(app_configs, **kwargs):
    if not hasattr(settings, "DJANGO_VIDEO_ENCODER_FORMATS"):
        return [checks.Error(f"No DJANGO_VIDEO_ENCODER_FORMATS defined in settings")]
    errors = []
    encoder_list = [format for format, __ in Format.VIDEO_CODEC_CHOICES]
    formats_list = settings.DJANGO_VIDEO_ENCODER_FORMATS
    for format in formats_list:
        if not "video_codec" in format:
            errors.append(
                checks.Error(f"Format dict {format} has no defined `video_codec`")
            )
            continue
        if not format["video_codec"] in encoder_list:
            errors.append(
                checks.Error(f"Requested codec {format['video_codec']} is not defined in {encoder_list}")
            )
    duplicates = [
        format for n, format in enumerate(formats_list) if format in formats_list[:n]
    ]
    for duplicate in duplicates:
        errors.append(
            checks.Error(
                f"Format dict {duplicate} is duplicated in settings.DJANGO_VIDEO_ENCODER_FORMATS"
            )
        )
