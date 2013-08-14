from models import StigUser, Place, Sticker, Comment
from rest_framework import serializers
from rest_framework.reverse import reverse

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = StigUser
		fields = ('id', 'fb_id', 'first_name', 'last_name', 'avatar')


class CommentSerializer(serializers.ModelSerializer):
	class Meta:
		model = Comment

class PlaceSerializer(serializers.ModelSerializer):
	comments = serializers.SerializerMethodField('get_place_comments')

	def get_place_comments(self, obj):
		return reverse('commentsforplace-list', 
			   args=[obj.pk], request=self.context['request'])

	class Meta:
		model = Place
		fields = ('id', 'name', 'image', 'description', 'geolocation', 'comments')