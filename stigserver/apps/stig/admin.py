from django.contrib.gis import admin
from stigserver.apps.stig.models import *

admin.site.register(StigUser)
admin.site.register(Place, admin.OSMGeoAdmin)
admin.site.register(Sticker)
admin.site.register(Comment)
