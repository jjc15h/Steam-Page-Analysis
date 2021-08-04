# TODO: Work on creating visuals in both Python and PowerBI

import requests
import time
import re
import csv
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver

# Global list of different categories. Easier than passing them through constantly
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

    scroll_pause_time = 0.5

    # Get scroll height
    last_height = browser.execute_script("return document.body.scrollHeight")

    # Controls for the amount of pages python scrolls through in a web page
    page_amt = 0
    while True:
        # Scroll down to bottom
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(scroll_pause_time)

        # Calculate new scroll height and compare with last scroll height
        new_height = browser.execute_script("return document.body.scrollHeight")
        page_amt = page_amt + 1
        if page_amt == 1:
            break
        # Originally 6

    soup = BeautifulSoup(browser.page_source, 'html.parser')

    new_category = []

    # Gathers all the game URL links from the web page. Stops when the end of page is encountered or limit is reached
    web_page_count = 0
    for div in soup.find_all("div", {"class": "search_results"}):
        for link in div.select("a"):
            new_category.append(link['href'])
            web_page_count = web_page_count + 1
            if web_page_count == 500:
                break

    return new_category


def get_store_data(store):
    response = requests.get(store)
    soup = BeautifulSoup(response.content, 'html.parser')
    not_found = False

    # If a game page has all of the attributes then we can collect its information
    if soup.find('span', attrs={'itemprop': 'name'}):
        if soup.find('span', attrs={'itemprop': 'description'}):
            if soup.find('div', attrs={'class': 'date'}):
                # Gets the name of the game
                game_name = soup.find('span', attrs={'itemprop': 'name'}).next
                name_list.append(game_name)
                print(game_name)

                # Gets the date the game first released
                date = soup.find('div', attrs={'class': 'date'}).next
                date_list.append(date)
                print(date)

                # Gets the review category of the game
                if soup.find('span', attrs={'class': 'game_review_summary not_enough_reviews'}) and \
                        soup.find('span', attrs={'itemprop': 'description'}):
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
                rev_amt = soup.find('meta', attrs={'itemprop': 'reviewCount'})
                review_amt_list.append(rev_amt['content'])
                print("Review Amt: " + rev_amt['content'])

                # Grabs the price of the game including sales if applicable
                if soup.find('div', attrs={'class': 'discount_original_price'}):
                    # Get the price
                    game_price = soup.find('div', attrs={'class': 'discount_original_price'}).next
                    print("Original: " + game_price, end=" ")
                    original_price_list.append(game_price)
                    game_price = soup.find('div', attrs={'class': 'discount_final_price'}).next
                    print("Discounted: " + game_price)
                    discount_price_list.append(game_price)
                else:
                    game_price = soup.find('meta', attrs={'itemprop': 'price'})
                    print("Original No sale: " + game_price["content"])
                    original_price_list.append(game_price["content"])
                    discount_price_list.append(0)
                # Note Free games show up as 0.00 as original

                # Gets Achievements
                if soup.find('div', attrs={'id': 'achievement_block'}) and soup.find('div', attrs={'class': 'block_title'}):
                    achievement_num = soup.find('div', attrs={'id': 'achievement_block'}).find('div', attrs={'class': 'block_title'}).next

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

                # Grabs the rating system from the game page
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

                # Finds out whether the item is a DLC or not
                if soup.findAll('div', attrs={'class': 'game_area_bubble game_area_dlc_bubble'}):
                    print("DLC: Y")
                    DLC.append('Y')
                else:
                    DLC.append('N')
                    print("DLC: N")

                # Finds out whether the item is in early access (Not finished yet) or not
                print("Early Access: ", end='')
                if soup.find_all('div', attrs={'class': 'early_access_header'}):
                    print("Y", end='\n\n')
                    Early_Access.append('Y')
                else:
                    print("N", end='\n\n')
                    Early_Access.append('N')


# When a page category is swept through, this function creates a csv sheet for that category
def organize_page(sheet_name):
    rows = zip(name_list, date_list, review_list, score_list, review_amt_list, original_price_list, discount_price_list,
               achievement_list, rating_category, DLC, Early_Access)
    tab = ["Name", "Date Released", "Review Category", "Review Score", "Review Amount", "Original Price",
           "Discounted Price", "Achievements listed", "Game Rating", "DLC?", "Early Access?"]
    with open(sheet_name, mode='w') as test_file:
        writers = csv.writer(test_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        writers.writerow(tab)
        for row in rows:
            writers.writerow(row)


# Goes to the steam category page and grabs the links into "New_List"
# Goes through each link and places info into separate lists before organizing them into their own csv files
# To add/change what the program gets and searches for, give it a different filtered url than the ones provided.

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

# Goes through all 8 csv files and combines them into one "Sum" file
writer = pd.ExcelWriter('sum.xlsx', engine='xlsxwriter')
data = pd.read_csv("Sheet1.csv", encoding='windows-1252')
data2 = pd.read_csv("Sheet2.csv", encoding='windows-1252')
data3 = pd.read_csv("Sheet3.csv", encoding='windows-1252')
data4 = pd.read_csv("Sheet4.csv", encoding='windows-1252')
data5 = pd.read_csv("Sheet5.csv", encoding='windows-1252')
data6 = pd.read_csv("Sheet6.csv", encoding='windows-1252')
data7 = pd.read_csv("Sheet7.csv", encoding='windows-1252')
data8 = pd.read_csv("Sheet8.csv", encoding='windows-1252')
data.to_excel(writer, sheet_name='Action', index=False)
data2.to_excel(writer, sheet_name='Role Playing', index=False)
data3.to_excel(writer, sheet_name='Strategy', index=False)
data4.to_excel(writer, sheet_name='Simulation', index=False)
data5.to_excel(writer, sheet_name='Indie', index=False)
data6.to_excel(writer, sheet_name='Sports', index=False)
data7.to_excel(writer, sheet_name='Puzzle', index=False)
data8.to_excel(writer, sheet_name='Horror', index=False)
writer.save()
