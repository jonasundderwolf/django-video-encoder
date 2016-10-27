# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_zencoder.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('django_zencoder', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Thumbnail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('object_id', models.PositiveIntegerField()),
                ('time', models.PositiveIntegerField(verbose_name='Time (s)')),
                ('width', models.PositiveIntegerField(verbose_name='Width', null=True)),
                ('height', models.PositiveIntegerField(verbose_name='Height', null=True)),
                ('image', models.ImageField(max_length=512, blank=True, null=True, upload_to=django_zencoder.models.thumbnail_upload_to)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
        migrations.AlterField(
            model_name='format',
            name='duration',
            field=models.PositiveIntegerField(verbose_name='Duration (ms)', null=True),
        ),
        migrations.AlterField(
            model_name='format',
            name='extra_info',
            field=models.TextField(verbose_name='Zencoder information (JSON)', blank=True),
        ),
        migrations.AlterField(
            model_name='format',
            name='format',
            field=models.CharField(max_length=255, choices=[('mp4-high', 'mp4-high'), ('mp4-low', 'mp4-low'), ('webm-high', 'webm-high'), ('webm-low', 'webm-low')]),
        ),
        migrations.AlterField(
            model_name='format',
            name='height',
            field=models.PositiveIntegerField(verbose_name='Height', null=True),
        ),
        migrations.AlterField(
            model_name='format',
            name='width',
            field=models.PositiveIntegerField(verbose_name='Width', null=True),
        ),
    ]
