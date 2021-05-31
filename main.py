import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

browser = webdriver.Chrome()
browser.get("https://store.steampowered.com/search/?sort_by=Released_DESC&os=win")
browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

#---
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
    if a == 5:
        break

#---

soup = BeautifulSoup(browser.page_source, 'html.parser')

new_category = []
i=0
for div in soup.find_all("div", {"class": "search_results"}):
    for link in div.select("a"):
        new_category.append(link['href'])
        i = i+1
        if i == 500:
            break

print(*new_category, sep='\n')
