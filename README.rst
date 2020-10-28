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

    DJANGO_VIDEO_ENCODER_FORMATS = [
        {'codec': 'h264'},  # full resolution if not specified
        {'codec': 'h264', 'width': 720, 'height': 404},
        {'codec': 'vp9'},  # full resolution if not specified
        {'codec': 'vp9', 'width': 720, 'height': 404},
    ]

And specific settings using the zencoder backend:

* Add `ZENCODER_API_KEY` and `ZENCODER_NOTIFICATION_SECRET`
* You may also specify `ZENCODER_REGION` (default: europe) to the most suitable for you

Tests
=====

Run tests with `tox`


Misc
====

To not be confused with the archived
`theonion/django-zencoder <https://github.com/theonion/django-zencoder>`_
which is installed as `zencoder`

See also similar project `escaped/django-video-encoding <https://github.com/escaped/django-video-encoding>`_
