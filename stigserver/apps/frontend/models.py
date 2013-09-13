from django.db import models

class Contact(models.Model):
	email = models.EmailField(unique=True)
	timestamp = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return self.email
