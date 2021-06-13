# TODO: Clean up the code to make it look semi-decent
# TODO: Figure out how to directly link to tablaeu or PowerBI for extra points

import requests
import time
import re
import csv
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver

name_list = []
date_list = []
review_list = []
score_list = []
review_amt_list = []
original_price_list = []
discount_price_list = []
achievement_list = []
rating_category = []
DLC = []
Early_Access = []


def store_category(link):
    browser = webdriver.Chrome()
    browser.get(link)
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Put function
    name_list.clear()
    date_list.clear()
    review_list.clear()
    score_list.clear()
    review_amt_list.clear()
    original_price_list.clear()
    discount_price_list.clear()
    achievement_list.clear()
    rating_category.clear()
    DLC.clear()
    Early_Access.clear()

    SCROLL_PAUSE_TIME = 0.5

    # Get scroll height
    last_height = browser.execute_script("return document.body.scrollHeight")
    a = 0
    while True:
        # Scroll down to bottom
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = browser.execute_script("return document.body.scrollHeight")
        a = a + 1
        if a == 1:
            break
        # Originally 6

    soup = BeautifulSoup(browser.page_source, 'html.parser')

    new_category = []
    i = 0
    for div in soup.find_all("div", {"class": "search_results"}):
        for link in div.select("a"):
            new_category.append(link['href'])
            i = i + 1
            if i == 500:
                break

    return new_category


def get_store_data(store):
    response = requests.get(store)
    soup = BeautifulSoup(response.content, 'html.parser')
    not_found = False

    # If a game page has all of the attributes then we can collect its information
    if soup.find('span', attrs={'itemprop': 'name'}):
        if soup.find('span', attrs={'itemprop': 'description'}):
            # Gets the name of the game
            game_name = soup.find('span', attrs={'itemprop': 'name'}).next
            name_list.append(game_name)
            print(game_name)

            # Gets the date the game first released
            date = soup.find('div', attrs={'class': 'date'}).next
            date_list.append(date)
            print(date)

            # Gets the review category of the game
            if soup.find('span', attrs={'class': 'game_review_summary not_enough_reviews'}) and soup.find('span',
                                                                                                          attrs={
                                                                                                              'itemprop': 'description'}):
                review_list.append("Not Enough Reviews")
                print("Not Enough Reviews")
                not_found = True
            else:
                game_review = soup.find('span', attrs={'itemprop': 'description'}).next
                review_list.append(game_review)
                print(game_review, end='\n')

            # Grabs the game review score
            if not_found:
                print("No Score")
                score_list.append(0)
            elif soup.find('span', attrs={'class': 'nonresponsive_hidden responsive_reviewdesc'}):
                div = soup.find_all("span", {'class': 'nonresponsive_hidden responsive_reviewdesc'})
                if len(div) == 2:
                    str1 = ""
                    for i in div[1]:
                        str1 += str(i)
                    str1 = str1.strip()
                    game_score2 = str1[2] + str1[3]
                    score_list.append(game_score2)
                    print(game_score2)
                else:
                    str1 = ""
                    for i in div[0]:
                        str1 += str(i)
                    str1 = str1.strip()
                    game_score2 = str1[2] + str1[3]
                    score_list.append(game_score2)
                    print(game_score2)

            # Grabs the review amount
            lol = soup.find('meta', attrs={'itemprop': 'reviewCount'})
            review_amt_list.append(lol['content'])
            print("Review Amt: " + lol['content'])

            # Grabs the price of the game including sales if applicable
            if soup.find('div', attrs={'class': 'discount_original_price'}):
                # Get the price
                all = soup.find('div', attrs={'class': 'discount_original_price'}).next
                print("Original: " + all, end=" ")
                original_price_list.append(all)
                all = soup.find('div', attrs={'class': 'discount_final_price'}).next
                print("Discounted: " + all)
                discount_price_list.append(all)
            else:
                all = soup.find('meta', attrs={'itemprop': 'price'})
                print("Original No sale: " + all["content"])
                original_price_list.append(all["content"])
                discount_price_list.append(0)
            # Note Free games show up as 0.00 as original

            # Gets Achievements
            if soup.find('div', attrs={'id': 'achievement_block'}) and soup.find('div', attrs={'class': 'block_title'}):
                achievement_num = soup.find('div', attrs={'id': 'achievement_block'}).find('div',attrs={'class': 'block_title'}).next
                achievement_num = achievement_num.strip()
                achievement_num = re.findall('\d+', achievement_num)
                if len(achievement_num) == 1:
                    achievement_num = list(map(int, achievement_num))
                    print(achievement_num[0], end="")
                    achievement_list.append(achievement_num[0])
                else:
                    achievement_list.append(0)
                    print("0", end="")
                print(" Achievements")
            else:
                achievement_list.append(0)
                print("0 Achievements")

            # Work on Rating System ( Figure out how to get the ratings from a link

            print("Rating: ", end='')
            if soup.find_all('div', attrs={'class': 'game_rating_icon'}):
                for a in soup.find_all('div', attrs={'class': 'game_rating_icon'}):
                    if a.img:
                        temp = ''.join(a.img['src'])
                        temp = temp.rsplit('/', 1)
                        if temp[1] == "m.png":
                            rating_category.append("Mature")
                            print("Mature")
                        elif temp[1] == "t.png":
                            rating_category.append("Teen")
                            print("Teen")
                        elif temp[1] == "e.png":
                            rating_category.append("Everyone")
                            print("Everyone")
                        elif temp[1] == "e10.png":
                            rating_category.append("Everyone 10+")
                            print("Everyone 10+")
                        elif temp[1] == "ao.png":
                            rating_category.append("Adult")
                            print("Adult")
                        elif temp[1] == "rp.png":
                            rating_category.append("Pending")
                            print("Pending")
            else:
                print("No Rating")
                rating_category.append("No Rating")

            if soup.findAll('div', attrs={'class': 'game_area_bubble game_area_dlc_bubble'}):
                print("DLC: Y")
                DLC.append('Y')
            else:
                DLC.append('N')
                print("DLC: N")

            print("Early Access: ", end='')
            if soup.find_all('div', attrs={'class': 'early_access_header'}):
                print("Y", end='\n\n')
                Early_Access.append('Y')
            else:
                print("N", end='\n\n')
                Early_Access.append('N')


def organize_page(sheet_name):
    rows = zip(name_list, date_list, review_list, score_list, review_amt_list, original_price_list, discount_price_list,
               achievement_list, rating_category, DLC, Early_Access)
    tab = ["Name", "Date Released", "Review Category", "Review Score", "Review Amount", "Original Price",
           "Discounted Price", "Achievements listed", "Game Rating", "DLC?", "Early Access?"]
    with open(sheet_name, mode='w') as test_file:
        writer = csv.writer(test_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        writer.writerow(tab)
        for row in rows:
            writer.writerow(row)


# Sorts by Top Selling Action
New_List = store_category("https://store.steampowered.com/search/?filter=topsellers&tags=19")

for i in New_List[:-4]:
    get_store_data(i)

organize_page("Sheet1.csv")

# Top Selling Role Playing
New_List = store_category("https://store.steampowered.com/search/?tags=122&filter=topsellers")

for i in New_List[:-4]:
    get_store_data(i)

organize_page("Sheet2.csv")

# Top selling Strategy
New_List = store_category("https://store.steampowered.com/search/?tags=9&filter=topsellers")

for i in New_List[:-4]:
    get_store_data(i)

organize_page("Sheet3.csv")

# Top selling Simulation
New_List = store_category("https://store.steampowered.com/search/?tags=599&filter=topsellers")

for i in New_List[:-4]:
    get_store_data(i)

organize_page("Sheet4.csv")

# Top selling Indie Games
New_List = store_category("https://store.steampowered.com/search/?tags=492&filter=topsellers")

for i in New_List[:-4]:
    get_store_data(i)

organize_page("Sheet5.csv")

# Top selling Sports
New_List = store_category("https://store.steampowered.com/search/?tags=701&filter=topsellers")

for i in New_List[:-4]:
    get_store_data(i)

organize_page("Sheet6.csv")

# Top selling Puzzle
New_List = store_category("https://store.steampowered.com/search/?tags=1664&filter=topsellers")

for i in New_List[:-4]:
    get_store_data(i)

organize_page("Sheet7.csv")

# Top selling Horror
New_List = store_category("https://store.steampowered.com/search/?tags=1667&filter=topsellers")

for i in New_List[:-4]:
    get_store_data(i)

organize_page("Sheet8.csv")

writer = pd.ExcelWriter('sum.xlsx', engine='xlsxwriter')
data = pd.read_csv("Sheet1.csv")
data2 = pd.read_csv("Sheet2.csv")
data3 = pd.read_csv("Sheet3.csv")
data4 = pd.read_csv("Sheet4.csv")
data5 = pd.read_csv("Sheet5.csv")
data6 = pd.read_csv("Sheet6.csv")
data7 = pd.read_csv("Sheet7.csv")
data8 = pd.read_csv("Sheet8.csv")
data.to_excel(writer, sheet_name='Action', index=False)
data2.to_excel(writer, sheet_name='Role Playing', index=False)
data3.to_excel(writer, sheet_name='Strategy', index=False)
data4.to_excel(writer, sheet_name='Simulation', index=False)
data5.to_excel(writer, sheet_name='Indie', index=False)
data6.to_excel(writer, sheet_name='Sports', index=False)
data7.to_excel(writer, sheet_name='Puzzle', index=False)
data8.to_excel(writer, sheet_name='Horror', index=False)
writer.save()
