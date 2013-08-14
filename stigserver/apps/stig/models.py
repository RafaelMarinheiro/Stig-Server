from django.contrib.gis.db import models

# Create your models here.
class StigUser(models.Model):
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	avatar = models.URLField()
	fb_id = models.CharField(max_length=20)

	def __unicode__(self):
		return "%s %s" % (self.first_name, self.last_name)


class Place(models.Model):
	name = models.CharField(max_length=100)
	image = models.URLField()
	description = models.TextField()
	geolocation = models.PointField(null=True, blank=True)

	objects = models.GeoManager()

	def __unicode__(self):
		return self.name


class Sticker(models.Model):
	name = models.CharField(max_length=50)
	image = models.URLField()

	def __unicode__(self):
		return self.name


class Comment(models.Model):
	place = models.ForeignKey(Place)
	user = models.ForeignKey(StigUser)
	content = models.TextField()
	stickers = models.ManyToManyField(Sticker)
	created_on = models.DateTimeField(auto_now_add=True)
	parent = models.ForeignKey('Comment', null=True, blank=True)

	def __unicode__(self):
		return "Comment #%d for %s by %s" % (self.pk, self.place, self.user)