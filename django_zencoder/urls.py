from django.conf.urls import patterns, url

from .views import notification

urlpatterns = patterns(
    'django_zencoder.views',
    url(r'notify/', notification, name='zencoder_notification'),
)
