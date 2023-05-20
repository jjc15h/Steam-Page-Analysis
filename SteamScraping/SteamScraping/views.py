# TODO: Create basic main page
# TODO: Consider using Steam news site
import csv
import os
import openpyxl
import datetime
from django.shortcuts import render
from datetime import datetime
from . models import Top_Games_Categories
from decimal import Decimal


def home_page(request):
    ctx = {}
    try:
        sum_excel_file = os.path.getmtime(os.getcwd() + "/SteamScraping/data_folder/sum.xlsx")
        ctx['last_modified'] = datetime.fromtimestamp(sum_excel_file).strftime('%Y-%m-%d %H:%M:%S')
    except FileNotFoundError:
        pass

    if request.POST:
        scrape_site(request)

    return render(request, 'steam_views/main_page.html', ctx)

# TODO: Use environment variables to shield password (Look on site to see if we can make happen)
# TODO: Rename the table to make more legible
# TODO: Maybe make threaded and work in the background?
def scrape_site(request):
    # Gathers info for the csv and Excel files to use in a bit
    #driver()

    # Deletes everything
    Top_Games_Categories.objects.all().delete()

    # TODO: After running, open each csv file and use a forloop to get and create a model object and then save or whatever
    # TODO: Make it so that it can take in all sheets instead of just one
    # Import csv data into Postgres Table
    workbook = openpyxl.load_workbook(os.getcwd() + "/SteamScraping/data_folder/sum.xlsx")
    sheet = workbook['Action']
    for row in sheet.iter_rows(min_row=2):
        print("EXAMPKLE:", type(row[8]).value)
        tgc = Top_Games_Categories()
        tgc.name = row[0].value
        tgc.developer = row[1].value
        tgc.publisher = row[2].value
        tgc.date_released = convert_to_datetime(row[3].value)
        tgc.review_category = row[4].value
        tgc.review_score = row[5].value
        tgc.metacritic_score = row[6].value
        tgc.review_amount = row[7].value
        tgc.original_price = convert_price(row[8].value)
        tgc.discounted_price = convert_price(row[9].value)
        tgc.achievements_listed = row[10].value
        tgc.game_rating = row[11].value
        tgc.dlc = convert_boolean(row[12].value)
        tgc.early_access = convert_boolean(row[13].value)
        tgc.category = row[14].value
        tgc.save()


# convert to datetime format
def convert_to_datetime(old_date):
    new_date = datetime.strptime(old_date, '%b %d, %Y')
    return new_date

def convert_boolean(val):
    if val == 'Y':
        return False
    else:
        return True

def convert_price(price):
    if price is None:
        new_price = None
    elif price == "0":
        new_price = "0.00"
    else:
        new_price = str(price)
        new_price = new_price[1:]

    return new_price