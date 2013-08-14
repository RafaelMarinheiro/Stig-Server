from models import StigUser, Place, Sticker, Comment, Checkin
from rest_framework import serializers
from rest_framework.reverse import reverse
from django.contrib.gis.geos import Point

class GeoPointField(serializers.WritableField):
	def to_native(self, obj):
		return {'lat': obj.x, 'lon': obj.y}

	def from_native(self, data):
		# raise Exception(data)
		return Point(data['lat'], data['lon'])

class UserSerializer(serializers.ModelSerializer):
	place = serializers.Field(source='get_place')

	class Meta:
		model = StigUser
		fields = ('id', 'fb_id', 'first_name', 'last_name', 'avatar', 'place')


class CommentSerializer(serializers.ModelSerializer):
	class Meta:
		model = Comment

class PlaceSerializer(serializers.ModelSerializer):
	stickers = serializers.Field(source='get_sticker_relevance')
	ranking = serializers.Field(source='get_ranking')
	location = GeoPointField(source='geolocation')

	class Meta:
		model = Place
		fields = ('id', 'name', 'image', 'description', 'location', 'stickers', 'ranking')


class CheckinSerializer(serializers.ModelSerializer):
	class Meta:
		model = Checkin
		fields = ('id', 'place', 'timestamp')