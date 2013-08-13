from common import *

DATABASES = {
    'default': {
         'ENGINE': 'django.contrib.gis.db.backends.postgis',
         'NAME': 'stigserver',
         'USER': 'postgres',
         'PASSWORD': '8ndBbIyd41W7ycK',
         'HOST': 'ec2-184-73-0-178.compute-1.amazonaws.com',   
     }
}