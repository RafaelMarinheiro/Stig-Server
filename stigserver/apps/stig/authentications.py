from rest_framework import authentication, exceptions
from models import StigUser
import base64

class FacebookStigAuthentication(authentication.BaseAuthentication):
	def authenticate(self, request):
		try:
			authorization_string = request.META.get('HTTP_AUTHORIZATION')
			authorization_string = authorization_string[6:]
			# print authorization_string
			authorization_string = base64.decodestring(authorization_string)
			fb_id, fb_access_token = authorization_string.split(':')
		except Exception, e:
			return None

		if not fb_id:
			return None

		try:
			user = StigUser.objects.get(fb_id=fb_id)
			valid = user.check_access_token(fb_access_token)
			if valid:
				return (None, user)
			else:
				raise exceptions.AuthenticationFailed('Invalid access token')
		except StigUser.DoesNotExist:
			raise exceptions.AuthenticationFailed('No such user')

	def authenticate_header(self, request):
		if request.method != 'POST':
			return 'Basic realm="api.stigapp.co"'
		else:
			super(FacebookStigAuthentication, self).authenticate_header(request)