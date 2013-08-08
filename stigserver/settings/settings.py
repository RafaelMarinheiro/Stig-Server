import os

if os.environ.has_key('PRODUCTION'):
	from stigserver.settings.production import *
else:
	from stigserver.settings.development import *