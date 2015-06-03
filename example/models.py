from django.db import models


class Video(models.Model):
    video_file = models.FileField()

    class Meta:
        app_label = 'example'
