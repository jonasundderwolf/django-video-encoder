import os.path
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from .api import encode


ZENCODER_MODELS = {}


def format_upload_to(instance, filename):
    dirname, original_filename = os.path.split(
        getattr(instance.video, instance.field_name).name)
    return 'formats/%s/%s/%s%s' % (
        instance.format,
        dirname or '.',
        slugify(os.path.splitext(original_filename)[0]),
        os.path.splitext(filename)[1].lower())


class Format(models.Model):
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType)

    video = GenericForeignKey()
    field_name = models.CharField(max_length=255)

    format = models.CharField(max_length=255, choices=[
        (f['label'], f['label']) for f in settings.ZENCODER_FORMATS])
    file = models.FileField(upload_to=format_upload_to, max_length=2048)
    width = models.PositiveIntegerField('Width', null=True)
    height = models.PositiveIntegerField('Height', null=True)
    duration = models.PositiveIntegerField('Duration (ms)', null=True)

    extra_info = models.TextField('Zencoder information (JSON)', blank=True)


def thumbnail_upload_to(instance, filename):
    return 'footage/thumbnails/%s/%s' % (
        'thumbnails',
        instance.video.pk,
        instance.time,
        os.path.splitext(filename)[1].lower()
    )

class Thumbnail(models.Model):
    time = models.PositiveIntegerField('Time (s)')
    width = models.PositiveIntegerField('Width', null=True)
    height = models.PositiveIntegerField('Height', null=True)
    image = models.ImageField(upload_to=thumbnail_upload_to, max_length=512, blank=True, null=True)

    video = models.GenericForeignKey()


def detect_file_changes(sender, instance, **kwargs):
    field = ZENCODER_MODELS.get('%s.%s' % (sender._meta.app_label, sender._meta.model_name))
    if field and hasattr(getattr(instance, field), 'file') and isinstance(
            getattr(instance, field).file, UploadedFile):
        if hasattr(instance, '_zencoder_updates'):
            instance._zencoder_updates.append(field)
        else:
            instance._zencoder_updates = [field]


def trigger_encoding(sender, instance, **kwargs):
    for field in getattr(instance, '_zencoder_updates', ()):
        encode(instance, field)


if getattr(settings, 'ZENCODER_MODELS', None):
    for name in settings.ZENCODER_MODELS:
        app_model, field = name.rsplit('.', 1)
        ZENCODER_MODELS[app_model.lower()] = field
    models.signals.pre_save.connect(detect_file_changes)
    models.signals.post_save.connect(trigger_encoding)
