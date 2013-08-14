# Create your views here.

from rest_framework import viewsets, generics
from serializers import UserSerializer, PlaceSerializer, CommentSerializer
from models import StigUser, Place, Sticker, Comment

class UserViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows users to be viewed or edited.
	"""
	queryset = StigUser.objects.all()
	serializer_class = UserSerializer


class PlaceViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows groups to be viewed or edited.
	"""
	queryset = Place.objects.all()
	serializer_class = PlaceSerializer


class CommentsForPlace(generics.ListCreateAPIView):
	queryset = Comment.objects.all()
	serializer_class = CommentSerializer

	def get_queryset(self):
		place_pk = self.kwargs['place_pk']
		return self.queryset.filter(place__pk=place_pk)

class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
	queryset = Comment.objects.all()
	serializer_class = CommentSerializer
