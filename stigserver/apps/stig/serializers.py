from models import StigUser, Place, Sticker, Comment, Checkin
from rest_framework import serializers
from rest_framework.parsers import JSONParser
from rest_framework.reverse import reverse
from django.contrib.gis.geos import Point

class GeoPointField(serializers.WritableField):
	def to_native(self, obj):
		return {'lat': obj.x, 'lon': obj.y}

	def from_native(self, data):
		if type(data) != dict:
			data = dict(data)
		return Point(data['lat'], data['lon'])

class FriendsListField(serializers.Field):
	def to_native(self, obj):
		if self.context['view'].request.auth is not None:
			friends = self.context['view'].request.auth.friends.all()
			friends = [f.pk for f in friends if f.get_place() == obj.pk]
			return friends
		return []


class UserSerializer(serializers.ModelSerializer):
	place = serializers.Field(source='get_place')
	first_name = serializers.CharField(read_only=True)
	last_name = serializers.CharField(read_only=True)
	avatar = serializers.CharField(read_only=True)
	access_token = serializers.CharField(source='access_token')

	class Meta:
		model = StigUser
		fields = ('id', 'fb_id', 'first_name', 'last_name', 'avatar', 'place', 'access_token')


class CommentSerializer(serializers.ModelSerializer):
	stickers = serializers.IntegerField(source='stickers')
	thumbs = serializers.Field(source='get_thumb_count')

	class Meta:
		model = Comment
		fields = ('id', 'stickers', 'place', 'user', 'content', 'created_on', 'parent', 'thumbs')


class PlaceSerializer(serializers.ModelSerializer):
	stickers = serializers.Field(source='get_sticker_relevance')
	ranking = serializers.Field(source='get_ranking')
	location = GeoPointField(source='geolocation')
	friends = FriendsListField(source='*')

	class Meta:
		model = Place
		fields = ('id', 'name', 'image', 'description', 'location', 'stickers', 'ranking', 'friends')


class CheckinSerializer(serializers.ModelSerializer):
	class Meta:
		model = Checkin
		fields = ('place', 'timestamp') # No ID.