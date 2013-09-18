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
		social = 0

		if self.context['view'].request.auth is not None:
			# Social
			user = self.context['view'].request.auth
			# modifier_avg = PlaceSticker.objects.filter(comment__user__friends__pk=user.pk, comment__place=obj).aggregate(modifier_avg=Avg('modifier'))['modifier_avg']
			stickers = Sticker.objects.all()
			relevance = {}
			for sticker in stickers:
				try:
					good = 0
					bad = 0
					for x in xrange(0,6):
						valid_until = datetime.now() - timedelta(days=x)
						valid_since = datetime.now() - timedelta(days=x+1)
						good_local = PlaceSticker.objects.filter(comment__user__friends__pk=user.pk, sticker=sticker, comment__place=self, modifier=PlaceSticker.MODIFIER_GOOD, comment__created_on__gt=valid_since, comment__created_on__lte=valid_until).count()
						bad_local = PlaceSticker.objects.filter(comment__user__friends__pk=user.pk, sticker=sticker, comment__place=self, modifier=PlaceSticker.MODIFIER_BAD, comment__created_on__gt=valid_since, comment__created_on__lte=valid_until).count()
						good += good_local * math.exp(-((x/3.5)**2))
						bad += bad_local * math.exp(-((x/3.5)**2))

					res = (((good - bad) / (good + bad)) + 1) * 0.5
				except ZeroDivisionError, e:
					res = 0
				if res is not None:
					name_encoded = sticker.name.lower()
					relevance[name_encoded] = res

			sticker_weigths = {
				'money': 0.125, # Money
				'food': 0.15, # Food
				'queue': 0.125, # Queue
				'music': 0.25, # Music
				'accessibility': 0.05, # Accessibility
				'people': 0.3, # People
			}

			for key in relevance:
				social += relevance[key] * sticker_weigths[key] * 1000


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