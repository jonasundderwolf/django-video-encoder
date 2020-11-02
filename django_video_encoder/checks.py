from django.conf import settings
from django.core import checks

from django_video_encoder.models import Format


@checks.register
def check__formats(app_configs, **kwargs):
    if not hasattr(settings, "DJANGO_VIDEO_ENCODER_FORMATS"):
        return [checks.Error("No DJANGO_VIDEO_ENCODER_FORMATS defined in settings")]
    errors = []
    encoder_list = [format for format, __ in Format.VIDEO_CODEC_CHOICES]
    for format in settings.DJANGO_VIDEO_ENCODER_FORMATS.values():
        if "video_codec" not in format:
            errors.append(
                checks.Error(f"Format dict {format} has no defined `video_codec`")
            )
            continue
        if not format["video_codec"] in encoder_list:
            errors.append(
                checks.Error(
                    f"Requested codec {format['video_codec']} is not defined in "
                    f"{encoder_list}"
                )
            )
    return errors
