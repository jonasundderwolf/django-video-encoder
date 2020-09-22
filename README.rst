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


Simple integration of a Django model with a FileField with zencoder.com

Requirements
============

Django 2.2+ (obviously) and celery to asynchronously run the encoding tasks.

Usage
=====

* Add `django_zencoder` to `INSTALLED_APPS`
* Add `ZENCODER_API_KEY` and `ZENCODER_NOTIFICATION_SECRET` to your settings file
* Set the `ZENCODER_THUMBNAIL_INTERVAL` in settings
* Add the desired formats in your settings file, i.e. ::
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
