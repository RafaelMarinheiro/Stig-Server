from models import StigUser, Place, Sticker, Comment, Checkin, PlaceSticker
from rest_framework import serializers
from rest_framework.parsers import JSONParser
from rest_framework.reverse import reverse
from django.contrib.gis.geos import Point
from django.db.models import Avg

class GeoPointField(serializers.WritableField):
	def to_native(self, obj):
		return {'lon': obj.x, 'lat': obj.y}

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


class RankingField(serializers.Field):
	def to_native(self, obj):
		ranking = obj.get_ranking()

		if self.context['view'].request.auth is not None:
			# Social
			user = self.context['view'].request.auth
			modifier_avg = PlaceSticker.objects.filter(comment__user__friends__pk=user.pk, comment__place=obj).aggregate(modifier_avg=Avg('modifier'))['modifier_avg']
			if modifier_avg is None:
				modifier_avg = 0
			social = modifier_avg * 1000

			ranking['social'] = social
			ranking['overall'] = (ranking['buzz'] + social) / 2
		return ranking


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
	# thumbs = serializers.Field(source='get_thumb_count')
	likes = serializers.Field(source='get_thumb_up')
	dislikes = serializers.Field(source='get_thumb_down')

	class Meta:
		model = Comment
		fields = ('id', 'stickers', 'place', 'user', 'content', 'created_on', 'parent', 'likes', 'dislikes')


class PlaceSerializer(serializers.ModelSerializer):
	stickers = serializers.Field(source='get_sticker_relevance')
	ranking = RankingField(source='*')
	location = GeoPointField(source='geolocation')
	friends = FriendsListField(source='*')

	class Meta:
		model = Place
		fields = ('id', 'name', 'image', 'description', 'location', 'stickers', 'ranking', 'friends')


class CheckinSerializer(serializers.ModelSerializer):
	class Meta:
		model = Checkin
		fields = ('place', 'timestamp') # No ID.