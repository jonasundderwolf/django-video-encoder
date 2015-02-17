from os.path import splitext
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from .api import encode


ZENCODER_MODELS = {}


class Format(models.Model):
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType)

    video = generic.GenericForeignKey()
    field_name = models.CharField(max_length=255)

    format = models.CharField(max_length=255, choices=[
        (f['label'], f['label']) for f in settings.ZENCODER_FORMATS])
    file = models.FileField(
        upload_to=lambda i, f: 'formats/%s/%s%s' % (
            i.format,
            splitext(getattr(i.video, i.field_name).name)[0],
            splitext(f)[1]),
        max_length=2048)
    width = models.PositiveIntegerField('Width', null=True)
    height = models.PositiveIntegerField('Height', null=True)
    duration = models.PositiveIntegerField('Duration (ms)', null=True)

    extra_info = models.TextField('Zencoder information (JSON)', blank=True)


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
