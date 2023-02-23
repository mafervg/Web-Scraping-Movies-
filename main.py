from bs4 import BeautifulSoup
import requests
import lxml
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import json
import time
import pandas as pd

URL = 'https://www.indiewire.com/gallery/50-best-movies-2022-critics-poll/mcdjafo-pa026/'


# HEADERS = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
#     "Accept-Language": "en-US,en;q=0.9"
# }

chrome_driver_path = "C:\Development\chromedriver.exe"
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service)

driver.get(URL)
time.sleep(30)
titles_elements = driver.find_elements(By.CLASS_NAME, 'c-gallery-vertical-slide__title')

titles = []

for title in titles_elements:
    titles.append(title.text)

titles_clean = []

for tit in titles:
    movie = tit.split(" ", 1)[1]
    titles_clean.append(movie[1:-1])
# print(titles_clean)

time.sleep(10)

directors = []
casts = []

for i in range(1, 51):
    directors_elements = driver.find_element(By.XPATH, f'//*[@id="pmc-gallery-vertical"]/div/div/div[{i}]/div/div[3]/p[1]').text
    directors.append(directors_elements)
    casts_elements = driver.find_element(By.XPATH, f'//*[@id="pmc-gallery-vertical"]/div/div/div[{i}]/div/div[3]/p[2]').text
    casts.append(casts_elements)
    time.sleep(1)

directors_list = []

for dir in directors:
    var = dir.split(' ', 1)[1]
    directors_list.append(var)

# print(directors_list)

cast_list = []

for cast in casts:
    names = cast.split('Cast:')
    try:
        if names[1]:
            cast_list.append(names[1].replace("\n", ", ").strip())
    except IndexError:
            cast_list.append("None")

# print(cast_list)

driver.quit()

df = pd.DataFrame({'movie_title': titles_clean, 'director': directors_list, 'cast': cast_list})
df.to_csv('50 best films of 2022.csv')
print(df)

