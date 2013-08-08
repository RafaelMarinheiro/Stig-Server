from tastypie import fields
from tastypie.resources import ModelResource
from models import *

class StigUserResource(ModelResource):
	class Meta:
		queryset = StigUser.objects.all()
		resource_name = 'user'


class PlaceResource(ModelResource):
	class Meta:
		queryset = Place.objects.all()
		resource_name = 'place'


class StickerResource(ModelResource):
	class Meta:
		queryset = Sticker.objects.all()
		resource_name = 'sticker'


class CommentResource(ModelResource):
	place = fields.ToOneField(PlaceResource, 'place')
	user = fields.ToOneField(StigUserResource, 'user')
	stickers = fields.ToManyField(StickerResource, 'stickers')
	parent = fields.ToOneField('CommentResource', 'parent', null=True)

	class Meta:
		queryset = Comment.objects.all()
		resource_name = 'comment'


