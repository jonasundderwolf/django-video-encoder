# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_video_encoder", "0002_auto_20161027_1629"),
    ]

    operations = [
        migrations.AlterField(
            model_name="format",
            name="format",
            field=models.CharField(
                max_length=255,
                choices=[
                    ("H.264 (HD)", "H.264 (HD)"),
                    ("H.264", "H.264"),
                    ("VP8 (HD)", "VP8 (HD)"),
                    ("VP8", "VP8"),
                ],
            ),
        ),
    ]
