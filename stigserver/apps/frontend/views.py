# Create your views here.

def home(request):
	context = {}
	return render(request, 'home.html', context)