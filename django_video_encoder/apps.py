from django.apps import AppConfig


class DjangoVideoEncoderConfig(AppConfig):
    name = "django_video_encoder"
    verbose_name = "Django Video Encoder"

    def ready(self):
        # Add System checks
        from .checks import check__formats  # NOQA
