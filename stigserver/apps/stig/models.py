from django.contrib.gis.db import models
from django.db.models import Avg, Sum
from open_facebook.api import OpenFacebook
from rest_framework.exceptions import PermissionDenied
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import transaction
from django.db.models import signals
from datetime import datetime, timedelta

# Create your models here.
class FacebookAccessToken(models.Model):
	user = models.ForeignKey('StigUser')
	access_token = models.TextField()
	trust_until = models.DateTimeField()

	def __unicode__(self):
		return u"Token for %s trusted until %s" % (self.user, self.trust_until)

class StigUser(models.Model):
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	avatar = models.URLField()
	fb_id = models.CharField(max_length=20, unique=True)
	friends = models.ManyToManyField('self')
	points = models.IntegerField(default=0)
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

	def update_friendships(self):
		graph = OpenFacebook(self.access_token)
		friends_request = graph.get('me', fields='friends')
		friends_list = friends_request['friends']['data']
		for friend in friends_list:
			try:
				user = StigUser.objects.get(fb_id=friend['id'])
				self.friends.add(user)
			except StigUser.DoesNotExist, e:
				pass # User not yet in Stig

	def save(self, *args, **kwargs):
		try:
			is_first = False
			if self.access_token and self.pk is None:
				is_first = True
				graph = OpenFacebook(self.access_token)
				me = graph.get('me', fields='id,first_name,last_name')
				self.first_name = me['first_name']
				self.last_name = me['last_name']
				self.avatar = 'https://graph.facebook.com/%s/picture?type=large' % me['id']

			super(StigUser, self).save(*args, **kwargs)
			if is_first:
				self.update_friendships()
				self.save()
		except Exception, e:
			raise PermissionDenied

	def check_access_token(self, access_token):
		try:
			token = FacebookAccessToken.objects.get(user=self, access_token=access_token, trust_until__gte=datetime.now())
			valid = True
		except FacebookAccessToken.DoesNotExist, e:
			try:
				graph = OpenFacebook(access_token)
				me = graph.get('me', fields='id')

				if self.fb_id == me['id']:
					token = FacebookAccessToken(user=self, access_token=access_token, trust_until=datetime.now() + timedelta(0, 10*60))
					token.save()
					valid = True
				else:
					valid = False
			except Exception, e:
				valid = False

		to_delete = FacebookAccessToken.objects.filter(trust_until__lt=datetime.now())
		to_delete.delete()

		return valid

	def can_see_details(self, other):
		return (self.pk == other.pk) or (self.pk in [f.pk for f in other.friends.all()])

	POINTS_CHECKIN = 3
	POINTS_COMMENT = 2
	POINTS_LIKED = 2
	POINTS_DISLIKED = -1

	@transaction.commit_manually()
	def punctuate(self, points):
		user = StigUser.objects.select_for_update().get(id=self.pk)
		user.points += points
		user.save()
		transaction.commit()


class Place(models.Model):
	name = models.CharField(max_length=100)
	image = models.URLField()
	description = models.TextField()
	geolocation = models.PointField(null=True, blank=True)

	objects = models.GeoManager()

	def __unicode__(self):
		return u"%s" % self.name

	def get_sticker_relevance(self, is_sum=True):
		stickers = Sticker.objects.all()
		result = {}
		valid_since = datetime.now() - timedelta(hours=12)
		for sticker in stickers:
			if is_sum:
				res = PlaceSticker.objects.filter(sticker=sticker, comment__place=self, comment__created_on__gte=valid_since).aggregate(modifier_sum=Sum('modifier'))['modifier_sum']
			else:
				try:
					res = (PlaceSticker.objects.filter(sticker=sticker, comment__place=self, modifier=PlaceSticker.MODIFIER_GOOD, comment__created_on__gte=valid_since).count()) / (PlaceSticker.objects.filter(sticker=sticker, comment__place=self, comment__created_on__gte=valid_since).count())
				except ZeroDivisionError, e:
					res = 0
			if res is not None:
				name_encoded = sticker.name.lower()
				result[name_encoded] = res
		return result

	def get_ranking(self):
		# Buzz
		sticker_weigths = {
			'money': 0.125, # Money
			'food': 0.15, # Food
			'queue': 0.125, # Queue
			'music': 0.25, # Music
			'accessibility': 0.05, # Accessibility
			'people': 0.3, # People
		}

		relevance = self.get_sticker_relevance(is_sum=False)
		buzz = 0

		for key in relevance:
			buzz += relevance[key] * sticker_weigths[key] * 1000

		# Social
		social = 0 # 0 if not authenticated

		# Overall
		overall = (buzz + social) / 2

		return {'buzz': int(buzz), 'social': social, 'overall': int(overall)}



class Sticker(models.Model):
	name = models.CharField(max_length=50)

	def __unicode__(self):
		return self.name


class PlaceSticker(models.Model):
	MODIFIER_BAD = -1
	MODIFIER_NEUTRAL = 0
	MODIFIER_GOOD = 1
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
	thumbs = generic.GenericRelation('Thumb')

	def get_thumb_count(self):
		thumbs = Thumb.objects.filter(content_type=ContentType.objects.get(app_label='stig', model='comment'), object_id=self.pk).aggregate(modifier_total=Sum('modifier'))['modifier_total']
		return thumbs or 0

	def get_thumb_up(self):
		thumbs = Thumb.objects.filter(content_type=ContentType.objects.get(app_label='stig', model='comment'), object_id=self.pk, modifier=Thumb.MODIFIER_UP).count()
		return thumbs or 0

	def get_thumb_down(self):
		thumbs = Thumb.objects.filter(content_type=ContentType.objects.get(app_label='stig', model='comment'), object_id=self.pk, modifier=Thumb.MODIFIER_DOWN).count()
		return thumbs or 0

	stickers_to_save = []

	sticker_infos = [
		(1, 0), # Money
		(2, 2), # Food
		(3, 4), # Queue
		(4, 6), # Music
		(5, 8), # Accessibility
		(6, 10), # People
	]

	modifier_infos = {
		-1: 1, # int("01", 2),
		0: 3, # int("11", 2),
		1: 2, # int("10", 2),
	}

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
					modifier = PlaceSticker.MODIFIER_BAD
				elif modifier_encoded == 2:
					modifier = PlaceSticker.MODIFIER_GOOD
				else:
					modifier = PlaceSticker.MODIFIER_NEUTRAL

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


def punctuate_comment(sender, **kwargs):
	if kwargs['created']:
		kwargs['instance'].user.punctuate(StigUser.POINTS_COMMENT)

signals.post_save.connect(punctuate_comment, sender=Comment)


class Thumb(models.Model):
	MODIFIER_UP = 1
	MODIFIER_DOWN = -1
	MODIFIER_CHOICES = (
		(MODIFIER_UP, 'Up'),
		(MODIFIER_DOWN, 'Down'),
	)
	modifier = models.IntegerField(choices=MODIFIER_CHOICES)
	created_on = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(StigUser)
	content_type = models.ForeignKey(ContentType)
	object_id = models.PositiveIntegerField()
	content_object = generic.GenericForeignKey('content_type', 'object_id')

	def __unicode__(self):
		return "Thumbs %s for %s by %s" % (self.get_modifier_display(), self.content_object, self.user)


def punctuate_thumb(sender, **kwargs):
	if kwargs['instance'].modifier == Thumb.MODIFIER_UP:
		kwargs['instance'].content_object.user.punctuate(StigUser.POINTS_LIKED)
	elif kwargs['instance'].modifier == Thumb.MODIFIER_DOWN:
		kwargs['instance'].content_object.user.punctuate(StigUser.POINTS_DISLIKED)

def undo_punctuate_thumb(sender, **kwargs):
	try:
		old_thumb = Thumb.objects.get(pk=kwargs['instance'].pk)
		if old_thumb.modifier == Thumb.MODIFIER_UP:
			old_thumb.content_object.user.punctuate(-StigUser.POINTS_LIKED)
		elif old_thumb.modifier == Thumb.MODIFIER_DOWN:
			old_thumb.content_object.user.punctuate(-StigUser.POINTS_DISLIKED)
	except Thumb.DoesNotExist:
		pass

signals.post_save.connect(punctuate_thumb, sender=Thumb)
signals.pre_save.connect(undo_punctuate_thumb, sender=Thumb)


class Checkin(models.Model):
	place = models.ForeignKey(Place)
	user = models.ForeignKey(StigUser)
	timestamp = models.DateTimeField(auto_now_add=True, editable=True)

	def __unicode__(self):
		return u"Checkin at %s by %s on %s" % (self.place, self.user, self.timestamp)

def punctuate_checkin(sender, **kwargs):
	if kwargs['created']:
		kwargs['instance'].user.punctuate(StigUser.POINTS_CHECKIN)

signals.post_save.connect(punctuate_checkin, sender=Checkin)


