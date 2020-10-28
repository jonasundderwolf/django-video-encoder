# Generated by Django 2.2.16 on 2020-10-28 14:43

from django.db import migrations, models

FULL_RESOLUTION = "full resolution"

format_mapping = {
    "H.264 (HD)": ("h264", True),
    "H.264": ("h264", False),
    "VP9 (HD)": ("vp9", True),
    "VP9": ("vp9", False),
}


def update_formats(apps, schema_editor):
    Format = apps.get_model("django_video_encoder", "Format")
    for format in Format.objects.all():
        format.video_codec, is_full_resolution = format_mapping.get(format.format, ("h264", False))
        resolution = (
            FULL_RESOLUTION if is_full_resolution else f"{format.width}x{format.height}"
        )
        format.format_label = f"{format.video_codec} ({resolution})"
        format.save()


class Migration(migrations.Migration):

    dependencies = [
        ("django_video_encoder", "0002_auto_20201022_1647"),
    ]

    operations = [
        migrations.AddField(
            model_name="format",
            name="format_label",
            field=models.CharField(default="", editable=False, max_length=80),
        ),
        migrations.AddField(
            model_name="format",
            name="video_codec",
            field=models.CharField(
                choices=[
                    ("h264", "h264"),
                    ("hevc", "hevc"),
                    ("jp2", "jp2"),
                    ("mpeg4", "mpeg4"),
                    ("theora", "theora"),
                    ("vp6", "vp6"),
                    ("vp8", "vp8"),
                    ("vp9", "vp9"),
                    ("wmv", "wmv"),
                ],
                default="h264",
                max_length=50,
            ),
        ),
        migrations.RunPython(update_formats, reverse_code=migrations.RunPython.noop),
    ]