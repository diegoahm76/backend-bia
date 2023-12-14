from django.shortcuts import render

from django.http import HttpResponse, Http404, HttpResponseRedirect

# Model
from transversal.models.base_models import Shortener

# Create your views here.
    
def redirect_url_view(request, shortened_part):
    try:
        shortener = Shortener.objects.get(short_url=shortened_part)
        shortener.save()
        
        return HttpResponseRedirect(shortener.long_url)
    except:
        raise Http404('El link no es válido')