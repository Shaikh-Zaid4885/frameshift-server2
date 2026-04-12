
from django.shortcuts import render
from django.http import HttpResponse
from .models import Item

def home(request):
    items = Item.objects.all()
    return render(request, 'home.html', {'items': items})

def about(request):
    return HttpResponse("About us")
