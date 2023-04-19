# TODO: Create basic main page
# TODO: Consider using Steam news site
from django.shortcuts import render

from . scrape_steam_platform import driver

def home_page(request):
    if request.POST:
        scrape_site(request)
    print("HELLO WORLD")
    return render(request, 'steam_views/main_page.html')

def scrape_site(request):
    print("WE'RE IN BUSINESS")
    driver()
    return render(request, 'steam_views/main_page.html')