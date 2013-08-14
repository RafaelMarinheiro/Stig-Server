from django.conf.urls import patterns, include, url
from stigserver.apps.stig import views

# Uncomment the next two lines to enable the admin:
from django.contrib.gis import admin
admin.autodiscover()

# API
# from tastypie.api import Api
# from stigserver.apps.stig.api import StigUserResource, PlaceResource, StickerResource, CommentResource
# v1_api = Api(api_name='v1')
# v1_api.register(StigUserResource())
# v1_api.register(PlaceResource())
# v1_api.register(StickerResource())
# v1_api.register(CommentResource())

# REST API
from rest_framework import routers
router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'places', views.PlaceViewSet)

# URLS

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    # (r'^api/', include(v1_api.urls)),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^places/(?P<place_pk>\d+)/comments/$', views.CommentsForPlace.as_view(), name='commentsforplace-list'),
    url(r'^places/(?P<place_pk>\d+)/comments/(?P<pk>\d+)/$', views.CommentDetail.as_view(), name='commentsforplace-detail'),
    url(r'^places/(?P<place_pk>\d+)/comments/(?P<parent_pk>\d+)/replies/$', views.RepliesForComment.as_view(), name='repliesforcomment-list'),
    url(r'^users/(?P<user_pk>\d+)/checkins/$', views.CheckinsForUser.as_view(), name='checkinsforuser-list'),
)
