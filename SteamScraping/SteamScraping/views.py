# TODO: Create basic main page
from django.shortcuts import render

def home_page(request):
    print("HELLO WORLD")
    return render(request, 'steam_views/main_page.html')