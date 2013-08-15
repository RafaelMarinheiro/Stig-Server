from django.contrib.gis.db import models
from django.db.models import Avg
from open_facebook.api import OpenFacebook
from rest_framework.exceptions import PermissionDenied

# Create your models here.
class StigUser(models.Model):
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	avatar = models.URLField()
	fb_id = models.CharField(max_length=20, unique=True)
	_access_token = ''

	def __unicode__(self):
		return u"%s %s" % (self.first_name, self.last_name)

	def get_place(self):
		try:
			last_checkin = Checkin.objects.filter(user=self).order_by('-timestamp')[0]
			return last_checkin.place.pk
		except IndexError:
			return None

	def get_access_token(self):
		return self._access_token

	def set_access_token(self, value):
		self._access_token = value

	access_token = property(get_access_token, set_access_token)

	def save(self, *args, **kwargs):
		try:
			graph = OpenFacebook(self.access_token)
			me = graph.get('me')
			self.first_name = me['first_name']
			self.last_name = me['last_name']
			self.avatar = 'https://graph.facebook.com/%s/picture?type=large' % me['id']
			super(StigUser, self).save(*args, **kwargs)
		except Exception, e:
			raise PermissionDenied


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
	comment = models.ForeignKey('Comment')

	def __unicode__(self):
		return u"Sticker %s (mod: %d)" % (self.sticker, self.modifier)


class Comment(models.Model):
	place = models.ForeignKey(Place)
	user = models.ForeignKey(StigUser)
	content = models.TextField()
	created_on = models.DateTimeField(auto_now_add=True)
	parent = models.ForeignKey('Comment', null=True, blank=True)
	stickers_to_save = []
	

	sticker_infos = [
		(1, 0), # Money
		(2, 2), # Food
		(3, 4), # Queue
		(4, 6), # Music
		(5, 8), # Accessibility
		(6, 10), # People
	]

	modifier_infos = [
		1, # int("01", 2),
		3, # int("11", 2),
		2, # int("10", 2),
	]

	def __unicode__(self):
		return u"Comment #%d for %s by %s" % (self.pk, self.place, self.user)

	def get_stickers(self):
		result = 0

		placestickers = PlaceSticker.objects.filter(comment=self)

		for sticker_info in self.sticker_infos:
			try:
				placesticker = placestickers.get(sticker_id=sticker_info[0])
				result = result | self.modifier_infos[placesticker.modifier] << sticker_info[1]
			except:
				pass

		return result

	def set_stickers(self, data):
		# PlaceSticker.objects.filter(comment=self).delete()
		self.stickers_to_save = []

		for sticker_info in self.sticker_infos:
			modifier_encoded = (data & (3 << sticker_info[1])) >> sticker_info[1]
			if modifier_encoded > 0:
				if modifier_encoded == 1:
					modifier = 0
				elif modifier_encoded == 2:
					modifier = 2
				else:
					modifier = 1

				placesticker = PlaceSticker(sticker_id=sticker_info[0], modifier=modifier)
				self.stickers_to_save.append(placesticker)
				# raise Exception(placesticker)


	stickers = property(get_stickers, set_stickers)

	def save(self, *args, **kwargs):
		super(Comment, self).save(*args, **kwargs)

		if (len(self.stickers_to_save) > 0):
			PlaceSticker.objects.filter(comment_id=self.id).delete()
			for sticker in self.stickers_to_save:
				sticker.comment_id = self.id
				sticker.save()


class Checkin(models.Model):
	place = models.ForeignKey(Place)
	user = models.ForeignKey(StigUser)
	timestamp = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return u"Checkin at %s by %s on %s" % (self.place, self.user, self.timestamp)




