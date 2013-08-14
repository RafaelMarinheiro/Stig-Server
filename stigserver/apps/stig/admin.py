from django.contrib.gis import admin
from stigserver.apps.stig.models import *

class PlaceStickerInline(admin.TabularInline):
    model = PlaceSticker
    extra = 1

class CommentAdmin(admin.ModelAdmin):
	inlines = (PlaceStickerInline, )

admin.site.register(StigUser)
admin.site.register(Place, admin.OSMGeoAdmin)
admin.site.register(Sticker)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Checkin)