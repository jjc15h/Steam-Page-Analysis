# TODO: Incorporate postgres
# TODO: Work on creating visuals in both Python and/or PowerBI and/or SAS
# TODO: Work on making it gathers EVERY link on the steam main page
# TODO: Work on figuring out why counter strike, a free game is not listed as such....
# TODO: Decide on path to take with displaying and hosting
# TODO: work on moving files to the django app stuff

import requests
import time
import re
import csv
import pandas as pd
# TODO: Depending on where this is being ran add a contency
from . scrape_helper_data import store_meta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(ChromeDriverManager().install())

VERBOSE = True


def store_category(link):
    browser = webdriver.Chrome()
    browser.get(link)

    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    scroll_pause_time = 0.5

    # Get scroll height
    browser.execute_script("return document.body.scrollHeight")

    # Controls for the amount of pages python scrolls through in a web page
    page_amt = 0
    while True:
        # Scroll down to bottom
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # TODO: Run it for everything so we can play in PowerBI later
        # TODO: Figure out how to make this wait correctly
        #WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,
        #                                                                   '#capacityGrid > table > tbody')))
        # Wait to load page
        time.sleep(scroll_pause_time)

        # Calculate new scroll height and compare with last scroll height
        browser.execute_script("return document.body.scrollHeight")
        page_amt = page_amt + 1
        if page_amt == 1:
            break
        # Originally 6

    soup = BeautifulSoup(browser.page_source, 'html.parser')

    game_page_links = []

    # Gathers all the game URL links from the web page. Stops when the end of page is encountered or limit is reached
    web_page_count = 0
    for div in soup.find_all("div", {"class": "search_results"}):
        for link in div.select("a"):
            game_page_links.append(link['href'])
            web_page_count = web_page_count + 1
            if web_page_count == 500:
                break

    return game_page_links


def get_store_data(store, sheet_meta_info):

    response = requests.get(store)
    soup = BeautifulSoup(response.content, 'html.parser')
    not_found = False


    # If a game page has all the attributes then we can collect its information
    if soup.find('span', attrs={'itemprop': 'name'}):
        if soup.find('span', attrs={'itemprop': 'description'}):
            if soup.find('div', attrs={'class': 'date'}):
                # Gets the name of the game
                game_name = soup.find('span', attrs={'itemprop': 'name'}).next
                sheet_meta_info['name_list'].append(game_name)

                # Gets the date the game first released
                date = soup.find('div', attrs={'class': 'date'}).next
                sheet_meta_info['date_list'].append(date)

                # Gets the review category of the game
                if soup.find('span', attrs={'class': 'game_review_summary not_enough_reviews'}) and \
                        soup.find('span', attrs={'itemprop': 'description'}):
                    sheet_meta_info['review_list'].append("not Enough Reviews")
                    not_found = True
                else:
                    game_review = soup.find('span', attrs={'itemprop': 'description'}).next
                    sheet_meta_info['review_list'].append(game_review)

                if soup.find('div', attrs={"id": "developers_list"}):
                    sheet_meta_info['developer'].append(soup.find('div', attrs={"id": "developers_list"}).find_next('a', href=True).text)
                else:
                    sheet_meta_info['developer'].append('Unknown')

                if soup.find('div', text = "Publisher:", attrs={'class': 'subtitle column'}):
                    sheet_meta_info['publisher'].append(soup.find('div', text = "Publisher:", attrs={'class': 'subtitle column'}).next.find_next('a', href=True).text)
                else:
                    sheet_meta_info['publisher'].append("Unknown")


                # Grabs the game review score
                if not_found:
                    sheet_meta_info['score_list'].append(None)
                elif soup.find('span', attrs={'class': 'nonresponsive_hidden responsive_reviewdesc'}):
                    div = soup.find_all("span", {'class': 'nonresponsive_hidden responsive_reviewdesc'})
                    if len(div) == 2:
                        str1 = ""
                        for i in div[1]:
                            str1 += str(i)
                        str1 = str1.strip()
                        game_score2 = str1[2] + str1[3]
                        sheet_meta_info['score_list'].append(game_score2)
                    else:
                        str1 = ""
                        for i in div[0]:
                            str1 += str(i)
                        str1 = str1.strip()
                        game_score2 = str1[2] + str1[3]
                        sheet_meta_info['score_list'].append(game_score2)

                # Grabs the metacritic score if there is one
                if soup.find('div', attrs={'id': 'game_area_metascore'}):
                    regex = re.compile('^score')
                    sheet_meta_info['metacritic_score_list'].append(soup.find('div', attrs={'id': 'game_area_metascore'}).find('div', attrs={'class': regex}).text.strip())
                else:
                    sheet_meta_info['metacritic_score_list'].append(None)

                # Grabs the review amount
                rev_amt = soup.find('meta', attrs={'itemprop': 'reviewCount'})
                sheet_meta_info['review_amt_list'].append(rev_amt['content'])

                # Grabs the price of the game including sales if applicable. Note Free games show up as 0.00 as original
                # TODO: Make this work with this game link????: https://store.steampowered.com/app/261570/Ori_and_the_Blind_Forest/
                if soup.find('div', attrs={'id': 'freeGameBtn'}):
                    sheet_meta_info['original_price_list'].append(0)
                    sheet_meta_info['discount_price_list'].append(None)
                elif soup.find('div', attrs={'class': 'game_area_purchase_game_wrapper'}).find('div', attrs={'class': 'discount_original_price'}):
                    sheet_meta_info['original_price_list'].append(soup.find('div', attrs={'class': 'game_area_purchase_game_wrapper'}).find('div', attrs={'class': 'discount_original_price'}).text.strip())
                    sheet_meta_info['discount_price_list'].append(soup.find('div', attrs={'class': 'game_area_purchase_game_wrapper'}).find('div', attrs={'class': 'discount_final_price'}).text.strip())
                elif soup.find('div', attrs={'class': 'game_area_purchase_game_wrapper'}).find('div', attrs={'class': 'game_purchase_price price'}):
                    sheet_meta_info['original_price_list'].append(soup.find('div', attrs={'class': 'game_area_purchase_game_wrapper'}).find('div', attrs={'class': 'game_purchase_price price'}).text.strip())
                    sheet_meta_info['discount_price_list'].append(None)
                elif soup.find('div', attrs={'class': 'discount_original_price'}):
                    # Get the price
                    game_price = soup.find('div', attrs={'class': 'discount_original_price'}).next
                    sheet_meta_info['original_price_list'].append(game_price)

                    game_price = soup.find('div', attrs={'class': 'discount_final_price'}).next
                    sheet_meta_info['discount_price_list'].append(game_price)
                else:
                    print("OPTION 3")
                    # Original No Sale
                    game_price = soup.find('meta', attrs={'itemprop': 'price'})
                    sheet_meta_info['original_price_list'].append(game_price["content"])
                    sheet_meta_info['discount_price_list'].append(None)

                # Gets Achievements
                if soup.find('div', attrs={'id': 'achievement_block'}) and soup.find('div', attrs={'class': 'block_title'}):
                    achievement_num = soup.find('div', attrs={'id': 'achievement_block'}).find('div', attrs={'class': 'block_title'}).next

                    achievement_num = achievement_num.strip()
                    achievement_num = re.findall('\d+', achievement_num)
                    if len(achievement_num) == 1:
                        achievement_num = list(map(int, achievement_num))
                        sheet_meta_info['achievement_list'].append(achievement_num[0])
                    else:
                        sheet_meta_info['achievement_list'].append(0)
                else:
                    sheet_meta_info['achievement_list'].append(0)

                # Grabs the rating system from the game page
                if soup.find_all('div', attrs={'class': 'game_rating_icon'}):
                    for a in soup.find_all('div', attrs={'class': 'game_rating_icon'}):
                        if a.img:
                            temp = ''.join(a.img['src'])
                            temp = temp.rsplit('/', 1)
                            if temp[1] == "m.png":
                                sheet_meta_info['rating_category'].append("Mature")
                            elif temp[1] == "t.png":
                                sheet_meta_info['rating_category'].append("Teen")
                            elif temp[1] == "e.png":
                                sheet_meta_info['rating_category'].append("Everyone")
                            elif temp[1] == "e10.png":
                                sheet_meta_info['rating_category'].append("Everyone 10+")
                            elif temp[1] == "ao.png":
                                sheet_meta_info['rating_category'].append("Adult")
                            elif temp[1] == "rp.png":
                                sheet_meta_info['rating_category'].append("Pending")
                else:
                    sheet_meta_info['rating_category'].append("No Rating")

                # Finds out whether the item is a DLC or not
                if soup.findAll('div', attrs={'class': 'game_area_bubble game_area_dlc_bubble'}):
                    sheet_meta_info['DLC'].append('Y')
                else:
                    sheet_meta_info['DLC'].append('N')

                # Finds out whether the item is in early access (Not finished yet) or not
                if soup.find_all('div', attrs={'class': 'early_access_header'}):
                    sheet_meta_info['Early_Access'].append('Y')
                else:
                    sheet_meta_info['Early_Access'].append('N')

    if VERBOSE:
        for blah in sheet_meta_info:
            print(blah, sheet_meta_info[blah][-1:])
        print("\n----------------\n")


# When a page category is swept through, this function creates a csv sheet for that category
def organize_page(sheet_name, meta_info):
    rows = zip(meta_info['name_list'], meta_info['developer'], meta_info['publisher'], meta_info['date_list'],
               meta_info['review_list'], meta_info['score_list'], meta_info['metacritic_score_list'],
               meta_info['review_amt_list'], meta_info['original_price_list'], meta_info['discount_price_list'],
               meta_info['achievement_list'], meta_info['rating_category'], meta_info['DLC'], meta_info['Early_Access'])
    tab = ["Name", "Developer", "Publisher", "Date Released", "Review Category", "Review Score", "MetaCritic Review Score",
           "Review Amount", "Original Price","Discounted Price", "Achievements listed", "Game Rating", "DLC?", "Early Access?"]
    with open(sheet_name, mode='w', encoding='utf-8') as test_file:
        writers = csv.writer(test_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        writers.writerow(tab)
        for row in rows:
            writers.writerow(row)


def driver():
    sheet_meta_info = dict()
    sheet_meta_info["developer"] = []
    sheet_meta_info["publisher"] = []
    sheet_meta_info["name_list"] = []
    sheet_meta_info["date_list"] = []
    sheet_meta_info["review_list"] = []
    sheet_meta_info["score_list"] = []
    sheet_meta_info["metacritic_score_list"] = []
    sheet_meta_info["review_amt_list"] = []
    sheet_meta_info["original_price_list"] = []
    sheet_meta_info["discount_price_list"] = []
    sheet_meta_info["achievement_list"] = []
    sheet_meta_info["rating_category"] = []
    sheet_meta_info["DLC"] = []
    sheet_meta_info["Early_Access"] = []
    failed_links = []
    # Goes to the steam category page and grabs the links into "New_List"
    # Goes through each link and places info into separate lists before organizing them into their own csv files
    # To add/change what the program gets and searches for, give it a different filtered url than the ones provided.

    # Goes through all 8 csv files and combines them into one "Sum" file
    writer = pd.ExcelWriter('SteamScraping/data_folder/sum.xlsx', engine='xlsxwriter')

    # Store_link, Category, Sheetname
    for info in store_meta:

        # Clear out the list for every game cateogry page link thing we open
        for cat_list in sheet_meta_info:
            sheet_meta_info[cat_list].clear()

        game_page_list = store_category(info['store_link'])

        # TODO: When we find an error remove the latest entry from the list and record it
        for game_link in game_page_list[:-4]:
            try:
                get_store_data(game_link, sheet_meta_info)
            except TypeError:
                failed_links.append(game_link)

        print("ALL FAILED LINKS:", failed_links)
        organize_page(info['sheet'], sheet_meta_info)

        data = pd.read_csv(info['sheet'], encoding='windows-1252')
        data.to_excel(writer, sheet_name=info['category'], index=False)

    writer.save()

if  __name__ == '__main__':
    driver()