from django.shortcuts import render, redirect, HttpResponse
from stigserver.apps.stig.models import Comment
from django.utils import simplejson
from django.db.models import Q

# Create your views here.

def home(request):
	context = {}
	return render(request, 'frontend/home.html', context)

def home_comment(request):
	comment = Comment.objects.all().order_by('?')[0]

	stickers = []
	for sticker in comment.placesticker_set.filter(~Q(modifier=0))[0:3]:
		stickers.append({
			'name': sticker.sticker.name.lower(),
			'modifier': 'positive' if sticker.modifier > 0 else 'negative',
		})

	obj = {
		'photo': comment.user.avatar,
		'name': "%s %s" % (comment.user.first_name, comment.user.last_name[0]),
		'place': comment.place.name,
		'comment': comment.content,
		'stickers': stickers,
	}
	return HttpResponse(simplejson.dumps(obj))