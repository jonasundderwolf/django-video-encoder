from django.conf.urls import url

from .views import notification

urlpatterns = [
    url(r'notify/', notification, name='zencoder_notification'),
]
