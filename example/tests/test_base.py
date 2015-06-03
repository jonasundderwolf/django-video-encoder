from django.test import TestCase
from django.test.utils import override_settings

from example.models import Video


class ZencoderTestCase(TestCase):

    @override_settings(ZENCODER_FORMATS={}):
    def test_create_format(self):
        """Create a video and see it being reformatted"""
        pass

