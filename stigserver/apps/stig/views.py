from rest_framework import viewsets, generics, permissions, authentication, status, mixins
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
import hashlib
from django.utils import simplejson

def etag_for(data):
	sha1 = hashlib.sha1()
	sha1.update(simplejson.dumps(data))
	return 'stig-%s' % sha1.hexdigest()

def unicode_dict(data):
	for key in data.keys():
		if type(data[key]) is not dict:
			data[key] = unicode(data[key])
		else:
			data[key] = unicode_dict(data[key])
	return key

def cached_response(request, response, ttl):
	# data = response.data.copy()
	# etag = etag_for(unicode_dict(data))
	
	# if etag == request.META.get('HTTP_IF_NONE_MATCH', None):
	# 	response = Response({}, status=status.HTTP_304_NOT_MODIFIED)

	# response['ETag'] = etag
	# response['Cache-Control'] = 'max-age=%s' % ttl

	return response

class UserViewSet(viewsets.ModelViewSet):
	authentication_classes = (FacebookStigAuthentication, )
	permission_classes = (FacebookStigPermission, )
	queryset = StigUser.objects.all()
	serializer_class = UserSerializer

	def list(self, request, *args, **kwargs):
		response = (super(viewsets.ModelViewSet, self)).list(request, *args, **kwargs)
		return cached_response(request, response, 2*60)

	def retrieve(self, request, *args, **kwargs):
		response = (super(viewsets.ModelViewSet, self)).retrieve(request, *args, **kwargs)
		return cached_response(request, response, 2*60)


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

	def list(self, request, *args, **kwargs):
		response = (super(viewsets.ModelViewSet, self)).list(request, *args, **kwargs)
		return cached_response(request, response, 2*60)

	def retrieve(self, request, *args, **kwargs):
		response = (super(viewsets.ModelViewSet, self)).retrieve(request, *args, **kwargs)
		return cached_response(request, response, 2*60)


class CommentsForPlace(generics.ListCreateAPIView):
	authentication_classes = (FacebookStigAuthentication, authentication.SessionAuthentication)
	permission_classes = (FacebookStigPermission, )
	queryset = Comment.objects.all()
	serializer_class = CommentSerializer

	def get_queryset(self):
		self.queryset = self.queryset.order_by('created_on')

		before = self.request.QUERY_PARAMS.get('before', None)
		stickers_filter = self.request.QUERY_PARAMS.get('filter', None)

		if before:
			self.queryset = self.queryset.filter(timestamp__lte=before)

		if stickers_filter:
			sticker_ids = []
			for i in xrange(1,7):
				if int(stickers_filter) & (1 << (i-1)) > 0:
					sticker_ids.append(i)

			for sticker_id in sticker_ids:
				self.queryset = self.queryset.filter(placesticker__sticker__pk=sticker_id, placesticker__modifier__in=[-1, 1])

		place_pk = self.kwargs['place_pk']
		try:
			Place.objects.get(pk=place_pk)
		except Place.DoesNotExist, e:
			raise Http404
		return self.queryset.filter(place__pk=place_pk)

	def pre_save(self, obj):
		obj.place = Place.objects.get(pk=self.kwargs['place_pk'])

		if self.request.auth is not None:
			obj.user = self.request.auth
		else:
			return Response({'error': 'You must athenticate.'}, status=status.HTTP_401_UNAUTHORIZED)

	def list(self, request, *args, **kwargs):
		response = (super(generics.ListCreateAPIView, self)).list(request, *args, **kwargs)
		return cached_response(request, response, 1*60)

	def retrieve(self, request, *args, **kwargs):
		response = (super(generics.ListCreateAPIView, self)).retrieve(request, *args, **kwargs)
		return cached_response(request, response, 1*60)



class RepliesForComment(generics.ListCreateAPIView):
	queryset = Comment.objects.all()
	serializer_class = CommentSerializer

	def get_queryset(self):
		parent_pk = self.kwargs['parent_pk']
		return self.queryset.filter(parent__pk=parent_pk)

	def list(self, request, *args, **kwargs):
		response = (super(generics.ListCreateAPIView, self)).list(request, *args, **kwargs)
		return cached_response(request, response, 1*60)

	def retrieve(self, request, *args, **kwargs):
		response = (super(generics.ListCreateAPIView, self)).retrieve(request, *args, **kwargs)
		return cached_response(request, response, 1*60)


class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
	queryset = Comment.objects.all()
	serializer_class = CommentSerializer

	def retrieve(self, request, *args, **kwargs):
		response = (super(generics.RetrieveUpdateDestroyAPIView, self)).retrieve(request, *args, **kwargs)
		return cached_response(request, response, 1*60)


class ThumbForComment(APIView):
	authentication_classes = (FacebookStigAuthentication, )
	permission_classes = (FacebookStigPermission, )

	def post(self, request, format=None, **kwargs):
		if self.request.auth is not None:
			try:
				comment = Comment.objects.get(pk=kwargs['comment_pk'])
			except Comment.DoesNotExist, e:
				raise Http404
			modifier = kwargs['modifier']

			try:
				thumb = Thumb.objects.get(content_type=ContentType.objects.get(app_label='stig', model='comment'), object_id=comment.pk, user=self.request.auth)
			except Thumb.DoesNotExist, e:
				thumb = Thumb(content_type=ContentType.objects.get(app_label='stig', model='comment'), object_id=comment.pk, user=self.request.auth)

			if thumb.modifier == modifier:
				thumb.delete()
			else:
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
			
			response = Response(serializer.data, status=status.HTTP_200_OK)
			return cached_response(request, response, 3*60)

		return Response({'error': 'You must athenticate.'}, status=status.HTTP_401_UNAUTHORIZED)


class CheckinAtPlace(APIView):
	authentication_classes = (FacebookStigAuthentication, )
	permission_classes = (FacebookStigPermission, )

	def post(self, request, format=None, **kwargs):
		if self.request.auth is not None:
			try:
				place = Place.objects.get(pk=kwargs['place_pk'])
			except Place.DoesNotExist, e:
				raise Http404

			checkin = Checkin(place=place, user=self.request.auth)
			checkin.save()
			
			return Response({'timestamp': checkin.timestamp}, status=status.HTTP_200_OK)

		return Response({'error': 'You must athenticate.'}, status=status.HTTP_401_UNAUTHORIZED)


class CheckinsForUser(generics.ListAPIView):
	authentication_classes = (FacebookStigAuthentication, )
	permission_classes = (FacebookStigPermission, )

	queryset = Checkin.objects.all()
	serializer_class = CheckinSerializer

	def get_queryset(self):
		user_pk = self.kwargs['user_pk']
		if (self.request.auth is not None) and (int(self.request.auth.pk) == int(user_pk)):
			user_pk = self.kwargs['user_pk']
			return self.queryset.filter(user__pk=user_pk)

		raise Http404

	def pre_save(self, obj):
		obj.user_id = self.kwargs['user_pk']

	def list(self, request, *args, **kwargs):
		response = (super(generics.ListAPIView, self)).list(request, *args, **kwargs)
		return cached_response(request, response, 1*60)