from django.shortcuts import render
from .models import Item


def test(request):
    items = Item.objects.all()
    return render(request, 'index.html')
