from django.conf.urls.defaults import patterns, include

urlpatterns = patterns('',
    (r'^forum/', include('djangobb_forum.urls', namespace='djangobb')),
)
