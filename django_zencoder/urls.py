from django.conf.urls import url

from .views import notification

urlpatterns = [
    'django_zencoder.views',
    url(r'notify/', notification, name='zencoder_notification'),
]
