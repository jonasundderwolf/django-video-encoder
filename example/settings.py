import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEBUG = True
TEMPLATE_DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "db.sqlite3",
    }
}

TIME_ZONE = "Europe/Berlin"
LANGUAGE_CODE = "en-us"

SITE_ID = 1

USE_I18N = True
USE_L10N = True
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATIC_ROOT = os.path.join(BASE_DIR, "static")
MEDIA_URL = "/media/"
STATIC_URL = "/static/"
SECRET_KEY = '0pfuvtvasasd8623123foobar76723"b)lna4*f_-xxkszs4##!+wpo'
ROOT_URLCONF = "example.urls"
TEMPLATE_DIRS = (os.path.join(BASE_DIR, "templates"),)

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.sites",
    "django_zencoder.apps.ZencoderConfig",
    "example",
]

ZENCODER_THUMBNAIL_INTERVAL = 20
ZENCODER_FORMATS = [
    {"label": "H.264", "codec": "h264", "width": 720, "height": 480},
]
