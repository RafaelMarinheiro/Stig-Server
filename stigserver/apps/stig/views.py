# Create your views here.

from rest_framework import viewsets, generics, permissions, authentication, status
from serializers import UserSerializer, PlaceSerializer, CommentSerializer, CheckinSerializer
from models import StigUser, Place, Sticker, Comment, Checkin, Thumb
from django.http import Http404
from authentications import FacebookStigAuthentication
from permissions import FacebookStigPermission
from django.db.models import Q
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import Point
import re

class UserViewSet(viewsets.ModelViewSet):
	authentication_classes = (FacebookStigAuthentication, )
	permission_classes = (FacebookStigPermission, )
	queryset = StigUser.objects.all()
	serializer_class = UserSerializer

	# def get_queryset(self):
	# 	return self.queryset.filter(Q(friends__pk=self.request.auth.pk))


class PlaceViewSet(viewsets.ModelViewSet):
	authentication_classes = (FacebookStigAuthentication, authentication.SessionAuthentication)
	permission_classes = (FacebookStigPermission, )
	queryset = Place.objects.all()
	serializer_class = PlaceSerializer

	def get_queryset(self):
		queryset = self.queryset

		search_query = self.request.QUERY_PARAMS.get('q', None)
		if search_query is not None:
			queryset = queryset.filter(name__icontains=search_query)

		geolocation = self.request.META.get('HTTP_GEOLOCATION', None)
		if geolocation is not None:
			lon, lat = re.match(r'geo:(\-?\d+\.\d+),(\-?\d+\.\d+)', geolocation).groups()
			# raise Exception(lon)
			point = Point(float(lon), float(lat))
			queryset = self.queryset.distance(point).order_by('distance')
		return queryset


class CommentsForPlace(generics.ListCreateAPIView):
	queryset = Comment.objects.all()
	serializer_class = CommentSerializer

	def get_queryset(self):
		self.queryset = self.queryset.order_by('created_on')

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


class ThumbForComment(APIView):
	authentication_classes = (FacebookStigAuthentication, )
	permission_classes = (FacebookStigPermission, )

	def post(self, request, format=None, **kwargs):
		if self.request.auth is not None:
			comment = Comment.objects.get(pk=kwargs['comment_pk'])
			modifier = kwargs['modifier']

			try:
				thumb = Thumb.objects.get(content_type=ContentType.objects.get(app_label='stig', model='comment'), object_id=comment.pk, user=self.request.auth)
			except Thumb.DoesNotExist, e:
				thumb = Thumb(content_type=ContentType.objects.get(app_label='stig', model='comment'), object_id=comment.pk, user=self.request.auth)

			thumb.modifier = modifier
			thumb.save()
			
			return Response({'thumbs': comment.get_thumb_count()}, status=status.HTTP_200_OK)

		return Response({'error': 'You must athenticate.'}, status=status.HTTP_401_UNAUTHORIZED)


class MySelf(APIView):
	authentication_classes = (FacebookStigAuthentication, )
	permission_classes = (FacebookStigPermission, )

	def get(self, request, format=None, **kwargs):
		if self.request.auth is not None:
			serializer = UserSerializer(self.request.auth)
			
			return Response(serializer.data, status=status.HTTP_200_OK)

		return Response({'error': 'You must athenticate.'}, status=status.HTTP_401_UNAUTHORIZED)


class CheckinsForUser(generics.ListCreateAPIView):
	queryset = Checkin.objects.all()
	serializer_class = CheckinSerializer

	def get_queryset(self):
		user_pk = self.kwargs['user_pk']
		return self.queryset.filter(user__pk=user_pk)

	def pre_save(self, obj):
		obj.user_id = self.kwargs['user_pk']