from common import *

DATABASES = {
    'default': {
         'ENGINE': 'django.contrib.gis.db.backends.postgis',
         'NAME': 'stig',
         'USER': 'Cisneiros',
         'HOST': 'localhost',   
     }
}

ROOT_URLCONF = 'stigserver.urls.local'

# A dictionary of urlconf module paths, keyed by their subdomain.
SUBDOMAIN_URLCONFS = {
    None: 'stigserver.urls.local',  # no subdomain, e.g. ``example.com``
}