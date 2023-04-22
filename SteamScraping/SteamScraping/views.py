# TODO: Create basic main page
# TODO: Consider using Steam news site
from django.shortcuts import render
from . scrape_steam_platform import driver
from datetime import datetime
import os

def home_page(request):
    ctx = {}
    sum_excel_file = os.path.getmtime(os.getcwd() + "/SteamScraping/data_folder/sum.xlsx")
    ctx['last_modified'] = datetime.fromtimestamp(sum_excel_file).strftime('%Y-%m-%d %H:%M:%S')

    if request.POST:
        scrape_site(request)

    return render(request, 'steam_views/main_page.html', ctx)

# TODO: Maybe make threaded and work in the background?
def scrape_site(request):
    driver()