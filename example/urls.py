from django.conf.urls import url

from django_video_encoder.views import notification

urlpatterns = [
    url(r"notify/", notification, name="zencoder_notification"),
]
