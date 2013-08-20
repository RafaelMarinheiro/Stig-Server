# Create your views here.

from rest_framework import viewsets, generics, permissions
from serializers import UserSerializer, PlaceSerializer, CommentSerializer, CheckinSerializer
from models import StigUser, Place, Sticker, Comment, Checkin
from django.http import Http404
from authentications import FacebookStigAuthentication
from permissions import FacebookStigPermission
from django.db.models import Q

class UserViewSet(viewsets.ModelViewSet):
	authentication_classes = (FacebookStigAuthentication, )
	permission_classes = (FacebookStigPermission, )
	queryset = StigUser.objects.all()
	serializer_class = UserSerializer

	def get_queryset(self):
		return self.queryset.filter(Q(friends__pk=self.request.auth.pk))


class PlaceViewSet(viewsets.ModelViewSet):
	authentication_classes = (FacebookStigAuthentication, )
	permission_classes = (FacebookStigPermission, )
	queryset = Place.objects.all()
	serializer_class = PlaceSerializer

	def get_queryset(self):
		queryset = self.queryset
		search_query = self.request.QUERY_PARAMS.get('q', None)
		if search_query is not None:
			queryset = queryset.filter(name__icontains=search_query)
		return queryset


class CommentsForPlace(generics.ListCreateAPIView):
	queryset = Comment.objects.all()
	serializer_class = CommentSerializer

	def get_queryset(self):
		before = self.request.QUERY_PARAMS.get('before', None)
		if before:
			self.queryset = self.queryset.filter(timestamp__lte=before)

		place_pk = self.kwargs['place_pk']
		try:
			Place.objects.get(pk=place_pk)
		except Exception, e:
			raise Http404
		return self.queryset.filter(place__pk=place_pk)

	def pre_save(self, obj):
		obj.place_id = self.kwargs['place_pk']


class RepliesForComment(generics.ListCreateAPIView):
	queryset = Comment.objects.all()
	serializer_class = CommentSerializer

	def get_queryset(self):
		parent_pk = self.kwargs['parent_pk']
		return self.queryset.filter(parent__pk=parent_pk)


class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
	queryset = Comment.objects.all()
	serializer_class = CommentSerializer


class CheckinsForUser(generics.ListCreateAPIView):
	queryset = Checkin.objects.all()
	serializer_class = CheckinSerializer

	def get_queryset(self):
		user_pk = self.kwargs['user_pk']
		return self.queryset.filter(user__pk=user_pk)

	def pre_save(self, obj):
		obj.user_id = self.kwargs['user_pk']