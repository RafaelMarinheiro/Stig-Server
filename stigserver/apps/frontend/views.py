#-*-encoding: utf8-*-

from django.shortcuts import render, redirect, HttpResponse
from stigserver.apps.stig.models import Comment
from django.utils import simplejson
from django.db.models import Q
from rest_framework import status
from models import *
from django.db import IntegrityError
from django import forms

def home(request):
	# if not request.user.is_authenticated():
	# 	return redirect('http://fb.com/stigapp')
	context = {}

	context['team_members'] = [
		{
			'name': 'Rafael Nunes',
			'photo': 'rafael-nunes.jpg',
			'position': 'Gerente Geral',
			'fb_id': 'peaonunes',
		},
		{
			'name': 'Rafael Marinheiro',
			'photo': 'rafael-marinheiro.jpg',
			'position': 'Gerente de Desenvolvimento',
			'fb_id': 'rafaelmarinheiro',
		},
		{
			'name': 'Fanny Chien',
			'photo': 'fanny.jpg',
			'position': 'Gerente de Usabilidade',
			'fb_id': 'fannychien93',
		},
		{
			'name': 'Alexandre Cisneiros',
			'photo': 'alexandre.jpg',
			'position': 'Desenvolvedor',
			'fb_id': 'Cisneiros',
		},
		{
			'name': 'Arthur Braga',
			'photo': 'arthur.jpg',
			'position': 'Designer',
			'fb_id': 'arthurbraga22',
		},
		{
			'name': 'Cecília Eloy',
			'photo': 'cecilia.jpg',
			'position': 'Designer',
			'fb_id': 'cecilia.eloy',
		},
		{
			'name': 'Diego Rodriges',
			'photo': 'diego.jpg',
			'position': 'Desginer',
			'fb_id': 'diego.rodrigues.5437923',
		},
		{
			'name': 'Gustavo Stor',
			'photo': 'gustavo.jpg',
			'position': 'Desenvolvedor',
			'fb_id': 'gstor',
		},
		{
			'name': 'Lucas Fernandes',
			'photo': 'lucas-fernandes.jpg',
			'position': 'Designer',
			'fb_id': 'lucas.fernandescorreia',
		},
		{
			'name': 'Lucas Tenório',
			'photo': 'lucas-tenorio.jpg',
			'position': 'Desenvolvedor',
			'fb_id': 'lucasvtenorio',
		},
		{
			'name': 'Luiz Vasconselos',
			'photo': 'luiz.jpg',
			'position': 'Desenvolvedor',
			'fb_id': 'luiz.vasconcelos.58',
		},
		{
			'name': 'Pedro Diniz',
			'photo': 'pedro.jpg',
			'position': 'Desenvolvedor',
			'fb_id': 'PedroHRDiniz32',
		},
		{
			'name': 'Pollyana Diniz',
			'photo': 'pollyana.jpg',
			'position': 'Administradora',
			'fb_id': 'dinizpollyanna',
		},
		{
			'name': "Raphael D'Emery",
			'photo': 'raphael.jpg',
			'position': 'Turismólogo',
			'fb_id': 'raphael.demery',
		},
		{
			'name': "Thomás Soares",
			'photo': 'thomas.jpg',
			'position': 'Designer',
			'fb_id': 'thomas.soares2',
		},
		{
			'name': "Camila Marinheiro",
			'photo': 'camila.jpg',
			'position': 'Divulgação',
			'fb_id': 'milamarinheiro',
		},
	]
	return render(request, 'frontend/home.html', context)

def home_comment(request):
	safe_ids = [8, 16, 25, 31, 64, 76, 130, 157]
	comment = Comment.objects.filter(~Q(content="")).filter(pk__in = safe_ids).order_by('?')[0]

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

def home_save_contact(request):
	class SaveContactForm(forms.Form):
		email = forms.EmailField()

	form = SaveContactForm(request.POST)
	if form.is_valid():
		email = form.cleaned_data['email']
		try:
			contact = Contact(email=email)
			contact.save()

			code = status.HTTP_200_OK
			content = {"email": contact.email, "timestamp": contact.timestamp.strftime("%c")}
		except IntegrityError, e:
			code = status.HTTP_400_BAD_REQUEST
			content = {"error": "You must inform an unique email address.", "internal_code": 1}
	else:
		code = status.HTTP_400_BAD_REQUEST
		content = {"error": "Invalid email address.", "internal_code": 2}

	

	return HttpResponse(simplejson.dumps(content), code)