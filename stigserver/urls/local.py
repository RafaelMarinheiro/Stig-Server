from django.conf.urls import patterns, include, url
import api, frontend

# URLS

urlpatterns = patterns('',
    url(r'^api/', include(api)),
    url(r'^frontend/', include(frontend)),
)
