from django.contrib.contenttypes import admin

from .models import Format


class FormatInline(admin.GenericTabularInline):
    model = Format
    fields = ("format_label", "video_codec", "file", "width", "height", "duration")
    readonly_fields = fields
    extra = 0
    max_num = 0
