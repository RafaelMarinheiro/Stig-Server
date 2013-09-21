from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib.gis import admin
admin.autodiscover()

# URLS

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'stigserver.apps.frontend.views.home', name='home'),
    url(r'^home_comment/$', 'stigserver.apps.frontend.views.home_comment', name='home_comment'),
    url(r'^home_save_contact/$', 'stigserver.apps.frontend.views.home_save_contact', name='home_save_contact'),
)

from stigserver.settings import settings

urlpatterns += patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
)