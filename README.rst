===============
django-zencoder
===============

.. image:: https://img.shields.io/pypi/v/django-zencoder.svg
    :target: https://pypi.python.org/pypi/django-zencoder

.. image:: https://img.shields.io/pypi/pyversions/django-zencoder.svg
    :target: https://pypi.python.org/pypi/django-zencoder

.. image:: https://img.shields.io/pypi/djversions/django-zencoder
    :alt: PyPI - Django Version
    :target: https://pypi.python.org/pypi/django-zencoder


Simple integration with zencoder.com

Upload videos and asynchronously store the encoded videos.

Requirements
============

Django 2.2+ and Celery to asynchronously run the encoding tasks.

Usage
=====

You will need to add the following to your django settings:

* Add `django_zencoder` to `INSTALLED_APPS`
* Add `ZENCODER_API_KEY` and `ZENCODER_NOTIFICATION_SECRET`
* Set the `ZENCODER_THUMBNAIL_INTERVAL`
* Add the desired formats, for example ::
    ZENCODER_FORMATS = [
        {'label': 'H.264 (HD)', 'codec': 'h264'},
        {'label': 'H.264', 'codec': 'h264', 'width': 720, 'height': 404},
        {'label': 'VP9 (HD)', 'codec': 'VP9'},
        {'label': 'VP9', 'codec': 'VP9', 'width': 720, 'height': 404},
    ]

Tests
=====

Run tests with `tox`


Misc
====

To not be confused with the archived
`theonion/django-zencoder <https://github.com/theonion/django-zencoder>`_
which is installed as `zencoder` (without django- prefix)
