from django.contrib.gis import admin
from stigserver.apps.stig.models import *
from django.contrib.contenttypes import generic

class PlaceStickerInline(admin.TabularInline):
    model = PlaceSticker
    extra = 1

class ThumbInline(generic.GenericTabularInline):
	model = Thumb
	extra = 1

class CommentAdmin(admin.ModelAdmin):
	inlines = (PlaceStickerInline, ThumbInline)

class FriendshipInline(admin.TabularInline):
    model = StigUser
    extra = 1

class StigUserAdmin(admin.ModelAdmin):
	# inlines = (FriendshipInline, )
	filter_horizontal = ('friends', )

admin.site.register(StigUser, StigUserAdmin)
admin.site.register(Place, admin.OSMGeoAdmin)
admin.site.register(Sticker)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Checkin)