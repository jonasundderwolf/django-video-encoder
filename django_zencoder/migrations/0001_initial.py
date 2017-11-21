# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import django_zencoder.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Format',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('field_name', models.CharField(max_length=255)),
                ('format', models.CharField(max_length=255, choices=[(b'mp4-high', b'mp4-high'), (b'mp4-low', b'mp4-low'), (b'webm-high', b'webm-high'), (b'webm-low', b'webm-low')])),
                ('file', models.FileField(max_length=2048, upload_to=django_zencoder.models.format_upload_to)),
                ('width', models.PositiveIntegerField(null=True, verbose_name=b'Width')),
                ('height', models.PositiveIntegerField(null=True, verbose_name=b'Height')),
                ('duration', models.PositiveIntegerField(null=True, verbose_name=b'Duration (ms)')),
                ('extra_info', models.TextField(verbose_name=b'Zencoder information (JSON)', blank=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
        ),
    ]
