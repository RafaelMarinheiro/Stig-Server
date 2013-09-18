from models import StigUser, Place, Sticker, Comment, Checkin, PlaceSticker, Thumb
from django.contrib.contenttypes.models import ContentType
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


class ThumbsByMeField(serializers.Field):
	def to_native(self, obj):
		if self.context['view'].request.auth is not None:
			me = self.context['view'].request.auth
			try:
				thumb = Thumb.objects.get(content_type=ContentType.objects.get(app_label='stig', model='comment'), object_id=obj.pk, user=me)
				return thumb.modifier
			except Thumb.DoesNotExist, e:
				return 0
		return 0


class RankingField(serializers.Field):
	def to_native(self, obj):
		ranking = obj.get_ranking()

		if self.context['view'].request.auth is not None:
			# Social
			user = self.context['view'].request.auth
			valid_since = datetime.now() - timedelta(days=7)
			# modifier_avg = PlaceSticker.objects.filter(comment__user__friends__pk=user.pk, comment__place=obj).aggregate(modifier_avg=Avg('modifier'))['modifier_avg']
			try:
				modifier_avg = (PlaceSticker.objects.filter(comment__user__friends__pk=user.pk, comment__place=obj, modifier=PlaceSticker.MODIFIER_GOOD, comment__created_on__gt=valid_since).count() / float(PlaceSticker.objects.filter(comment__user__friends__pk=user.pk, comment__place=obj, comment__created_on__gt=valid_since).count()))
			except ZeroDivisionError, e:
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
	points = serializers.CharField(read_only=True)
	access_token = serializers.CharField(source='access_token')

	class Meta:
		model = StigUser
		fields = ('id', 'fb_id', 'first_name', 'last_name', 'avatar', 'place', 'points', 'access_token')


class PlaceSerializer(serializers.ModelSerializer):
	stickers = serializers.Field(source='get_sticker_relevance')
	ranking = RankingField(source='*')
	location = GeoPointField(source='geolocation')
	friends = FriendsListField(source='*')

	class Meta:
		model = Place
		fields = ('id', 'name', 'image', 'description', 'location', 'stickers', 'ranking', 'friends')


class CommentSerializer(serializers.ModelSerializer):
	stickers = serializers.IntegerField(source='stickers')
	thumbs_by_me = ThumbsByMeField(source='*')
	likes = serializers.Field(source='get_thumb_up')
	dislikes = serializers.Field(source='get_thumb_down')
	place = serializers.PrimaryKeyRelatedField(required=False)
	user = serializers.PrimaryKeyRelatedField(required=False)

	class Meta:
		model = Comment
		fields = ('id', 'stickers', 'place', 'user', 'content', 'created_on', 'parent', 'likes', 'dislikes', 'thumbs_by_me')

	def validate(self, attrs):
		if 'place' not in attrs.keys() or attrs['place'] is None:
			attrs['place'] = Place.objects.get(pk=self.context['view'].kwargs['place_pk'])
			# pass
		if 'user' not in attrs.keys() or attrs['user'] is None:
			if self.context['view'].request.auth is not None:
				attrs['user'] = self.context['view'].request.auth

			# pass

		return attrs


class CheckinSerializer(serializers.ModelSerializer):
	class Meta:
		model = Checkin
		fields = ('place', 'timestamp') # No ID.