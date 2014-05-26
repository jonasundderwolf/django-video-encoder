from django.conf.urls import patterns, url

urlpatterns = patterns(
    'django_zencoder.views',
    url(r'notify/(\d+)/', 'notification', name='zencoder_notification'),
)
