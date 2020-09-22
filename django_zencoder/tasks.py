from celery import shared_task

from .api import get_video


@shared_task
def get_video_task(*args, **kwargs):
    get_video(*args, **kwargs)
