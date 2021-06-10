# Lets do this by tags and categories like action, strategy, etc... instead
#TODO: Clean up the code to make it look semi-decent
#TODO: Create an extra function for the workbook part.
#TODO: Work on combining multiple workbooks into one at the end
#TODO: Figure out how to directly link to tablaeu or PowerBI for extra points

import requests
import time
import re
import csv
from bs4 import BeautifulSoup
from selenium import webdriver

name_list = []
date_list = []
review_list=[]
score_list =[]
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
        if a == 2:
            break
        #Originally 6

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

    # If a game page has all of the attribtues then we can collect its information
    if soup.find('span', attrs={'itemprop': 'name'}):
        if soup.find('span', attrs={'itemprop': 'description'}):
            # Gets the name of the game
            game_name = soup.find('span', attrs={'itemprop': 'name'}).next
            name_list.append(game_name)
            print(game_name)

            #Gets the date the game first released
            date = soup.find('div', attrs={'class':'date'}).next
            date_list.append(date)
            print(date)

            # Gets the review category of the game
            if soup.find('span', attrs={'class': 'game_review_summary not_enough_reviews'}) and soup.find('span', attrs={'itemprop': 'description'}):
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

            #Grabs the review amount
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
                GELLO = soup.find('div', attrs={'id': 'achievement_block'}).find('div',
                                                                                 attrs={'class': 'block_title'}).next
                GELLO = GELLO.strip()
                GELLO = re.findall('\d+', GELLO)
                if len(GELLO) == 1:
                    GELLO = list(map(int, GELLO))
                    print(GELLO[0], end="")
                    achievement_list.append(GELLO[0])
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

    # Game Feature Tags Ex, Controller Support (?)
    # Operating Systems (?)

    # https://store.steampowered.com/app/1264280/Slipways/
    # https://store.steampowered.com/app/601840/Griftlands/
    # https://store.steampowered.com/app/1328670/Mass_Effect_Legendary_Edition/
    # "https://store.steampowered.com/app/211820/Starbound/"
    # "https://store.steampowered.com/app/322330/Dont_Starve_Together/" Achievements


# Sorts by Top Selling Action
New_List = store_category("https://store.steampowered.com/search/?tags=19&filter=topsellers")

for i in New_List[:-4]:
    get_store_data(i)

#get_store_data("https://store.steampowered.com/app/1420300/No_More_Heroes_2_Desperate_Struggle/")

# Sorts by Top Sellers
# Top_List = store_category("https://store.steampowered.com/search/?filter=topsellers&os=win")

# Sorts by Upcoming
# Upcoming_List = store_category("https://store.steampowered.com/search/?filter=comingsoon&os=win")

# Sorts by Special
# Special_List = store_category("https://store.steampowered.com/search/?&specials=1")

rows = zip(name_list,date_list,review_list,score_list,review_amt_list, original_price_list, discount_price_list, achievement_list,rating_category,DLC,Early_Access)
tab = ["Name","Date Released","Review Category", "Review Score", "Review Amount", "Original Price", "Discounted Price", "Achievements listed", "Game Rating", "DLC?", "Early Access?"]
with open("Test.csv", mode='w') as test_file:
    writer = csv.writer(test_file, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    writer.writerow(tab)
    for row in rows:
        writer.writerow(row)

# At the end here, be sure to combine multiple workbooks into a single one with multiple file sheets.