from django.conf.urls.defaults import *

from apps.captcha import views

urlpatterns = patterns('',
    (r'^captcha/(?P<captcha_id>\w+)/$', views.captcha_image),
)

