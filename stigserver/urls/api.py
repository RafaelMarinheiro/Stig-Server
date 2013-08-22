from django.conf.urls import patterns, include, url
from stigserver.apps.stig import views

# Uncomment the next two lines to enable the admin:
# from django.contrib.gis import admin
# admin.autodiscover()

# REST API
from rest_framework import routers
router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'places', views.PlaceViewSet)

# URLS

urlpatterns = patterns('',
    (r'^facebook/', include('django_facebook.urls')),
    # (r'^api/', include(v1_api.urls)),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^places/(?P<place_pk>\d+)/comments/$', views.CommentsForPlace.as_view(), name='commentsforplace-list'),
    url(r'^places/(?P<place_pk>\d+)/comments/(?P<pk>\d+)/$', views.CommentDetail.as_view(), name='commentsforplace-detail'),
    url(r'^places/(?P<place_pk>\d+)/comments/(?P<comment_pk>\d+)/like/$', views.ThumbForComment.as_view(), name='thumbforcomment-like', kwargs={'modifier':1}),
    url(r'^places/(?P<place_pk>\d+)/comments/(?P<comment_pk>\d+)/dislike/$', views.ThumbForComment.as_view(), name='thumbforcomment-dislike', kwargs={'modifier':-1}),
    url(r'^places/(?P<place_pk>\d+)/comments/(?P<parent_pk>\d+)/replies/$', views.RepliesForComment.as_view(), name='repliesforcomment-list'),
    url(r'^users/(?P<user_pk>\d+)/checkins/$', views.CheckinsForUser.as_view(), name='checkinsforuser-list'),
)
