from rest_framework import permissions

class FacebookStigPermission(permissions.BasePermission):
	def has_permission(self, request, view):
		if request.method == 'POST':
			return True
			
		if not request.auth:
			return False

		return True

	def has_object_permission(self, request, view, obj):
		if not request.auth:
			return False

		return request.auth.can_see_details(obj)
		