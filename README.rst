====================
django-video-encoder
====================

.. image:: https://img.shields.io/pypi/v/django-video-encoder.svg
    :target: https://pypi.python.org/pypi/django-video-encoder

.. image:: https://img.shields.io/pypi/pyversions/django-video-encoder.svg
    :target: https://pypi.python.org/pypi/django-video-encoder

.. image:: https://img.shields.io/pypi/djversions/django-video-encoder
    :alt: PyPI - Django Version
    :target: https://pypi.python.org/pypi/django-video-encoder


Simple integration with video encoding backends.

For now only the remote zencoder.com is supported.

Upload videos and asynchronously store the encoded videos and
the generated thumbnails.

Requirements
============

Django 2.2+ and Celery to asynchronously run the encoding tasks.

Usage
=====

You will need to add the following to your django settings:

* Add `django_video_encoder` to `INSTALLED_APPS`
* Add generic relation fields to your video models ::

    formats = GenericRelation(Format)
    thumbnails = GenericRelation(Thumbnail)

* Set the `DJANGO_VIDEO_ENCODER_THUMBNAIL_INTERVAL`
* Add the desired formats, for example ::

    DJANGO_VIDEO_ENCODER_FORMATS = {
        "H264 (HD)": {"video_codec": "h264"},  # full resolution if not specified
        "H264": {"video_codec": "h264", "width": 720, "height": 404},
        "VP9 (HD)": {"video_codec": "vp9"},
        "VP9": {"video_codec": "vp9", "width": 720, "height": 404},
    }

And specific settings using the zencoder backend:

* Add `ZENCODER_API_KEY` and `ZENCODER_NOTIFICATION_SECRET`
* You may also specify `ZENCODER_REGION` (default: europe) to the most suitable for you

`DJANGO_VIDEO_ENCODER_FORMATS` is a dictionary of
`{format_label: format_kwargs}` where `format_kwargs` is a
dictionary requiring `video_codec` and where all arguments are
added to the encoding job POST. You can define width, height and
much more see the
`Zencoder API <https://zencoder.support.brightcove.com/references/reference.html#operation/createJob>`_.

Tests
=====

Run tests with `tox`


Misc
====

To not be confused with the archived
`theonion/django-zencoder <https://github.com/theonion/django-zencoder>`_
which is installed as `zencoder`

See also similar project `escaped/django-video-encoding <https://github.com/escaped/django-video-encoding>`_
