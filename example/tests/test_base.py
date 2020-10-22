from unittest import mock

from django.core.files import File
from pytest import mark

from django_video_encoder.api import encode
from example.models import Video


@mark.django_db
def test_encode_called(mocker):
    """Assert encode will try to send data via the api"""
    file_mock = mock.MagicMock(spec=File)
    file_mock.name = "video.vid"
    mocked_send_request = mocker.patch("django_video_encoder.api.send_request")
    video_obj = Video(video_file=file_mock)
    encode(video_obj, "video_file")
    assert mocked_send_request.called
