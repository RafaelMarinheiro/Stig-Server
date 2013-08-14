from tastypie import fields
from tastypie.contrib.gis.resources import ModelResource
from models import *
from django.conf.urls import *
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.authorization import Authorization



class StigUserResource(ModelResource):
	class Meta:
		queryset = StigUser.objects.all()
		resource_name = 'user'


class StickerResource(ModelResource):
	class Meta:
		queryset = Sticker.objects.all()
		resource_name = 'sticker'


class PlaceResource(ModelResource):
	comments = fields.ToManyField('stigserver.apps.stig.api.CommentResource', 'comment_set', null=True)

	class Meta:
		queryset = Place.objects.all()
		resource_name = 'place'


class CommentResource(ModelResource):
	place = fields.ToOneField(PlaceResource, 'place')
	user = fields.ToOneField(StigUserResource, 'user')
	stickers = fields.ToManyField(StickerResource, 'stickers', null=True)
	parent = fields.ToOneField('stigserver.apps.stig.api.CommentResource', 'parent', null=True)

	class Meta:
		queryset = Comment.objects.all()
		resource_name = 'comment'
		filtering = {
			'place': ALL_WITH_RELATIONS,
		}
		authorization = Authorization()