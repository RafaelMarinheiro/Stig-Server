from django.contrib.gis.db import models
from django.db.models import Avg

# Create your models here.
class StigUser(models.Model):
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	avatar = models.URLField()
	fb_id = models.CharField(max_length=20)

	def __unicode__(self):
		return u"%s %s" % (self.first_name, self.last_name)

	def get_place(self):
		try:
			last_checkin = Checkin.objects.filter(user=self).order_by('-timestamp')[0]
			return last_checkin.place.pk
		except IndexError:
			return None


class Place(models.Model):
	name = models.CharField(max_length=100)
	image = models.URLField()
	description = models.TextField()
	geolocation = models.PointField(null=True, blank=True)

	objects = models.GeoManager()

	def __unicode__(self):
		return u"%s" % self.name

	def get_sticker_relevance(self):
		stickers = Sticker.objects.all()
		result = {}
		for sticker in stickers:
			avg = PlaceSticker.objects.filter(sticker=sticker, comment__place=self).aggregate(modifier_avg=Avg('modifier'))['modifier_avg']
			if avg:
				result[sticker.id] = avg
		return result

	def get_ranking(self):
		return {'social': 500, 'buzz': 500, 'overall': 500}


class Sticker(models.Model):
	name = models.CharField(max_length=50)
	image = models.URLField()

	def __unicode__(self):
		return self.name


class PlaceSticker(models.Model):
	MODIFIER_BAD = 0
	MODIFIER_NEUTRAL = 1
	MODIFIER_GOOD = 2
	MODIFIER_CHOICES = (
		(MODIFIER_BAD, 'Bad'),
		(MODIFIER_NEUTRAL, 'Neutral'),
		(MODIFIER_GOOD, 'Good'),
	)

	sticker = models.ForeignKey(Sticker)
	modifier = models.IntegerField(choices=MODIFIER_CHOICES)
	comment = models.ForeignKey('Comment', null=True)

	def __unicode__(self):
		return u"Sticker %s for Comment #%d (mod: %d)" % (self.sticker, self.comment.pk, self.modifier)


class Comment(models.Model):
	place = models.ForeignKey(Place)
	user = models.ForeignKey(StigUser)
	content = models.TextField()
	created_on = models.DateTimeField(auto_now_add=True)
	parent = models.ForeignKey('Comment', null=True, blank=True)

	def __unicode__(self):
		return u"Comment #%d for %s by %s" % (self.pk, self.place, self.user)


class Checkin(models.Model):
	place = models.ForeignKey(Place)
	user = models.ForeignKey(StigUser)
	timestamp = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return u"Checkin at %s by %s on %s" % (self.place, self.user, self.timestamp)
