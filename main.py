# Lets do this by tags and categories like action, strategy, etc... instead
import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver


def store_category(link):
    browser = webdriver.Chrome()
    browser.get(link)
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # ---
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
        if a == 6:
            break

    soup = BeautifulSoup(browser.page_source, 'html.parser')

    new_category = []
    i = 0
    for div in soup.find_all("div", {"class": "search_results"}):
        for link in div.select("a"):
            new_category.append(link['href'])
            i = i+1
            if i == 500:
                break

    return new_category


def get_store_data(store):
    response = requests.get(store)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Gets the name of the game. If we get to a page that doesn't have a name ready. Skip.
    if soup.find('span', attrs={'itemprop': 'name'}):
        game_name = soup.find('span', attrs={'itemprop': 'name'}).next
        print(game_name)


    #Gets the score of the game
    if soup.find('span', attrs={'class': 'nonresponsive_hidden responsive_reviewdesc'}):
        game_score = soup.find('span', attrs={'class': 'nonresponsive_hidden responsive_reviewdesc'}).next
        game_score2 = game_score[16] + game_score[17]
        print(game_score2)

    #Gets the review category of the game
    if soup.find('span', attrs={'itemprop': 'description'}):
        game_review = soup.find('span', attrs={'itemprop': 'description'}).next
        print(game_review, end='\n\n')




    #Lets get the Review Percentage

    # To find the price Work on Later
    # all = soup.find('meta', attrs={'itemprop':'price'})
    # all2 = all.get('content', '')
    # print(all2)
    # https://store.steampowered.com/app/1264280/Slipways/
    # https://store.steampowered.com/app/601840/Griftlands/


# Sorts by New and Trending
New_List = store_category("https://store.steampowered.com/search/?tags=19&filter=topsellers")

for i in New_List[:-4]:
    get_store_data(i)

#get_store_data("https://store.steampowered.com/app/1264280/Slipways/")




# Sorts by Top Sellers
# Top_List = store_category("https://store.steampowered.com/search/?filter=topsellers&os=win")

# Sorts by Upcoming
# Upcoming_List = store_category("https://store.steampowered.com/search/?filter=comingsoon&os=win")

# Sorts by Special
# Special_List = store_category("https://store.steampowered.com/search/?&specials=1")
