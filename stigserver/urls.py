from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib.gis import admin
admin.autodiscover()

# API
from tastypie.api import Api
from stigserver.apps.stig.api import StigUserResource, PlaceResource, StickerResource, CommentResource
v1_api = Api(api_name='v1')
v1_api.register(StigUserResource())
v1_api.register(PlaceResource())
v1_api.register(StickerResource())
v1_api.register(CommentResource())


# URLS

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    (r'^api/', include(v1_api.urls)),
)
