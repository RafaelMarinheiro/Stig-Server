from django.contrib.gis import admin
from stigserver.apps.stig.models import *

class PlaceStickerInline(admin.TabularInline):
    model = PlaceSticker
    extra = 1

class CommentAdmin(admin.ModelAdmin):
	inlines = (PlaceStickerInline, )

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