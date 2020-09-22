# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_zencoder", "0003_auto_20161031_1017"),
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
                    ("VP9 (HD)", "VP9 (HD)"),
                    ("VP9", "VP9"),
                ],
            ),
        ),
    ]
