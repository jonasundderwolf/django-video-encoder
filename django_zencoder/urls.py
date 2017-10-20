from django.conf.urls import url

urlpatterns = [
    'django_zencoder.views',
    url(r'notify/', 'notification', name='zencoder_notification'),
]
